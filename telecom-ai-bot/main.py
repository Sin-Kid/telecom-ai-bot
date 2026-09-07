"""
TeleBot AI — Fully Local Telecom Assistant
Brain : Llama 3.2 via Ollama
Voice : AI4Bharat Indic-Parler-TTS (trained on IndicVoices-R)
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional
import os
import json
import requests
import subprocess
import logging
import csv
import time
from datetime import datetime
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
import tts_engine
import whisper
import base64
import tempfile

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Self-Healing: Clear Port 8000 ──────────────────────────────────────────
def clear_port(port):
    try:
        # Find process ID (PID) using the port
        result = subprocess.check_output(["lsof", "-ti", f":{port}"]).decode().strip()
        if result:
            for pid in result.split("\n"):
                logger.info(f"Closing existing process {pid} on port {port}...")
                os.system(f"kill -9 {pid}")
    except Exception:
        pass # Port is likely already clear

# Run port clearing before anything else
clear_port(8000)

# ── Configuration ──────────────────────────────────────────────────────────

OLLAMA_URL   = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = "llama3.2"
API_HOST     = os.getenv("API_HOST", "0.0.0.0")
API_PORT     = int(os.getenv("API_PORT", 8000))

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "kn": "Kannada",
}

# Google Translate language codes for each supported language
GOOGLE_LANG_CODES = {
    "en": "en",
    "hi": "hi",
    "te": "te",
    "kn": "kn",
}

# ── Lifespan ───────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("TeleBot AI  —  FULL LOCAL MODE")
    logger.info(f"Brain : Ollama / {OLLAMA_MODEL}")
    logger.info("Voice : Local FastPitch + HiFi-GAN (Indic-TTS)")
    logger.info("=" * 60)
    yield
    logger.info("TeleBot AI shutting down.")

# ── App ────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="TeleBot AI",
    description="Fully Local Multilingual Telecom Assistant",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (CSS, JS)
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# ── Pydantic Models ────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    text: str
    language: str = "en"
    user_id: str = "default_user"
    phone: str = "6360341569"  # phone number to look up customer profile
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    bot_response: str
    language: str
    timestamp: str
    session_id: Optional[str] = None

class TTSRequest(BaseModel):
    text: str
    language: str = "en"

class STTRequest(BaseModel):
    audio_content: str
    mime_type: Optional[str] = "audio/webm"
    language: Optional[str] = "en"

# ── Customer Database ──────────────────────────────────────────────────────

def load_customers() -> dict:
    """Load customers.json and return a phone→customer lookup dict."""
    try:
        db_path = os.path.join(os.path.dirname(__file__), "customers.json")
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {c["phone"]: c for c in data.get("customers", [])}
    except Exception as e:
        logger.warning(f"Could not load customers.json: {e}")
        return {}

CUSTOMER_DB = load_customers()
logger.info(f"✅ Loaded {len(CUSTOMER_DB)} customer profiles.")

def get_customer(phone: str) -> dict:
    """Return customer dict for given phone, or default (Pavan) profile."""
    return CUSTOMER_DB.get(phone, CUSTOMER_DB.get("6360341569", {}))

# ── Ollama Logic ───────────────────────────────────────────────────────────

def get_base_system_prompt() -> str:
    try:
        prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.txt")
        with open(prompt_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return (
            "You are a helpful Telecom AI Assistant. "
            "Help users with balance enquiries, recharge plans, and complaints. "
            "Be concise, friendly, and accurate."
        )

def build_system_prompt(customer: dict) -> str:
    """Build a personalized system prompt injecting customer profile data."""
    base = get_base_system_prompt()
    if not customer:
        return base
    # Overwrite the CUSTOMER INFO block dynamically
    profile_block = f"""
### CUSTOMER INFO (FOR CURRENT SESSION):
- Name: {customer.get('name', 'Customer')}
- Phone: {customer.get('phone', 'Unknown')}
- Telecom Operator: {customer.get('operator', 'Airtel')}
- Plan: {customer.get('plan', 'Unknown')}
- Plan Validity: {customer.get('validity_days', 28)} days
- Daily Data Limit: {customer.get('data_per_day_gb', 2)} GB/day
- Data Remaining Today: {customer.get('data_remaining_gb', 0)} GB (out of {customer.get('data_per_day_gb', 2)} GB daily limit)
- Voice Benefit: {customer.get('voice', 'Unlimited Calls')}
- Bill Due: ₹{customer.get('bill_due', 0):.2f}
"""
    # Replace the existing CUSTOMER INFO block in the base prompt
    import re
    updated = re.sub(
        r'### CUSTOMER INFO.*?(?=###|$)', profile_block + "\n",
        base, flags=re.DOTALL
    )
    return updated if updated != base else (base + profile_block)

# ── Google Translation Bridge ──────────────────────────────────────────────

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
_translate_executor = ThreadPoolExecutor(max_workers=2)
TRANSLATION_TIMEOUT = 5  # seconds

def _do_translate(source: str, target: str, text: str) -> str:
    return GoogleTranslator(source=source, target=target).translate(text)

def translate_to_english(text: str, source_lang: str) -> str:
    """Translate text from source_lang to English. Gives up after 5s."""
    if source_lang == "en":
        return text
    try:
        gl_code = GOOGLE_LANG_CODES.get(source_lang, source_lang)
        future = _translate_executor.submit(_do_translate, gl_code, "en", text)
        translated = future.result(timeout=TRANSLATION_TIMEOUT)
        logger.info(f"🌐 [{source_lang}→en]: '{text[:40]}' → '{translated[:40]}'")
        return translated or text
    except FuturesTimeoutError:
        logger.warning(f"Translation [{source_lang}→en] timed out. Using original.")
        return text
    except Exception as e:
        logger.warning(f"Translation to English failed: {e}. Using original text.")
        return text

def translate_from_english(text: str, target_lang: str) -> str:
    """Translate English to target_lang. Gives up after 5s and returns English."""
    if target_lang == "en":
        return text
    try:
        gl_code = GOOGLE_LANG_CODES.get(target_lang, target_lang)
        future = _translate_executor.submit(_do_translate, "en", gl_code, text)
        translated = future.result(timeout=TRANSLATION_TIMEOUT)
        logger.info(f"🌐 [en→{target_lang}]: '{text[:40]}' → '{translated[:40]}'")
        return translated or text
    except FuturesTimeoutError:
        logger.warning(f"Translation [en→{target_lang}] timed out. Returning English.")
        return text
    except Exception as e:
        logger.warning(f"Translation from English failed: {e}. Returning English response.")
        return text

def ask_ollama(user_message_en: str, customer: dict = None) -> str:
    """Send an English message to Ollama and get an English response."""
    system_prompt = build_system_prompt(customer or {})

    payload = {
        "model": OLLAMA_MODEL,
        "system": system_prompt + "\n\nIMPORTANT: Always respond in English only. Be concise and helpful.",
        "prompt": f"User: {user_message_en}\nAssistant:",
        "stream": False,
        "options": {"temperature": 0.7, "top_p": 0.9},
    }

    try:
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=45)
        resp.raise_for_status()
        return resp.json().get("response", "I am processing your request…")
    except requests.exceptions.ConnectionError:
        return "⚠️ Ollama is not running. Please start it with: ollama serve"
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return "Sorry, I had trouble reaching my local brain. Please try again."

# ── CSV Reporting ──────────────────────────────────────────────────────────
REPORT_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "customer_reports.csv"))

def log_interaction(user_id, query, response, language, duration):
    file_exists = os.path.isfile(REPORT_FILE)
    with open(REPORT_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "User ID", "Language", "User Query", "Bot Response", "Duration (s)"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_id,
            language,
            query,
            response,
            f"{duration:.2f}"
        ])

# ── Routes ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    engine = tts_engine._engine_instance
    tts_ready = (len(engine.synthesizers) == 4) if engine else False
    return {
        "status": "ready",
        "mode": "fully_local",
        "tts_loaded": tts_ready,
        "ollama_model": OLLAMA_MODEL,
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    start_time = time.time()
    logger.info(f"[{message.language}] phone={message.phone} {message.text}")

    # Look up customer profile by phone number
    customer = get_customer(message.phone)
    logger.info(f"👤 Customer: {customer.get('name', 'Unknown')} | {customer.get('operator', 'Unknown')}")

    # Step 1: Translate user input → English (so llama3.2 fully understands it)
    user_text_en = translate_to_english(message.text, message.language)

    # Step 2: Ask Ollama in English with customer's profile injected
    bot_response_en = ask_ollama(user_text_en, customer)

    # Step 3: Translate Ollama's English response → user's language
    bot_text = translate_from_english(bot_response_en, message.language)

    duration = time.time() - start_time
    log_interaction(message.user_id, message.text, bot_text, message.language, duration)

    return ChatResponse(
        bot_response=bot_text,
        language=message.language,
        timestamp=datetime.now().isoformat(),
        session_id=message.session_id,
    )

@app.get("/customers")
async def list_customers():
    """Return all customer profiles (for demo/admin use)."""
    return {"total": len(CUSTOMER_DB), "customers": list(CUSTOMER_DB.values())}

@app.get("/lookup/{phone}")
async def lookup_customer(phone: str):
    """Look up a customer by phone number. Used by the onboarding screen."""
    customer = CUSTOMER_DB.get(phone)
    if customer:
        return {
            "found": True,
            "name": customer["name"],
            "operator": customer["operator"],
            "phone": customer["phone"],
        }
    return {"found": False}

# Pre-load Whisper and TTS models at boot time on the main thread (takes ~45-60s)
# This avoids runtime lag and prevents macOS background throttling.
logger.info("🔄 Pre-loading local TTS engines (en, hi, te, kn)...")
engine = tts_engine.get_engine()
for lang in ["en", "hi", "te", "kn"]:
    engine._load_model_for_lang(lang)
logger.info("✅ All TTS engines loaded successfully.")

stt_model = None  # Whisper loads lazily on first STT request

@app.post("/speech-to-text")
async def speech_to_text(request: STTRequest):
    try:
        audio_b64 = request.audio_content
        mime_type = request.mime_type or "audio/webm"

        if not audio_b64:
            return {"transcript": "", "error": "No audio content"}

        # Decode base64
        try:
            audio_data = base64.b64decode(audio_b64)
        except Exception as e:
            logger.error(f"STT: Base64 decode failed: {e}")
            return {"transcript": "", "error": "Invalid audio encoding"}

        # Pick correct extension so ffmpeg (inside Whisper) can decode it
        ext = ".webm" if "webm" in mime_type else ".ogg" if "ogg" in mime_type else ".wav"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_audio:
            temp_audio.write(audio_data)
            temp_audio.flush()
            temp_path = temp_audio.name

        logger.info(f"STT: {len(audio_data)} bytes | format={ext} | file={temp_path}")

        try:
            global stt_model
            if stt_model is None:
                logger.info("🔄 Loading Whisper model (first STT request)...")
                stt_model = whisper.load_model("base")
                logger.info("✅ Whisper model loaded.")
            
            # Map input language code directly to Whisper's language code
            whisper_lang = request.language if request.language in ["en", "hi", "te", "kn"] else None
            
            stt_prompts = {
                "kn": "ಕನ್ನಡ, ಮೊಬೈಲ್, ಬ್ಯಾಲೆನ್ಸ್, ರೀಚಾರ್ಜ್, ಪ್ಲಾನ್, ನೆಟ್‌ವರ್ಕ್",
                "te": "తెలుగు, మొబైల్, బ్యాలెన్స్, రీఛార్జ్, ప్లాన్, నెట్‌వర్క్",
                "hi": "हिंदी, मोबाइल, बैलेंस, रिचार्ज, प्लान, नेटवर्क",
                "en": "Hello, telecom support, balance, plan, recharge, network"
            }
            initial_prompt = stt_prompts.get(whisper_lang) if whisper_lang else None
            
            logger.info(f"🎤 STT: transcribing with forced language: {whisper_lang} and prompt: {initial_prompt}")
            
            result = stt_model.transcribe(
                temp_path, 
                fp16=False, 
                language=whisper_lang,
                initial_prompt=initial_prompt
            )
            transcript = result.get("text", "").strip()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        logger.info(f"🎤 STT: '{transcript}'")
        return {"transcript": transcript}

    except Exception as e:
        logger.error(f"STT Error: {e}")
        return {"transcript": "", "error": str(e)}

@app.post("/text-to-speech")
async def text_to_speech(request: TTSRequest):
    engine = tts_engine.get_engine()
    if not engine.is_ready:
        raise HTTPException(status_code=503, detail="TTS model is still loading. Please wait a moment.")

    audio_b64 = engine.generate_voice(request.text, request.language)
    if audio_b64:
        return {"audio_content": audio_b64, "language": request.language}

    raise HTTPException(status_code=500, detail="Audio generation failed.")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"error": "An internal error occurred."})

# ── Entry Point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    # HTTP is sufficient — http://localhost is a secure context in all browsers
    # (microphone works without HTTPS on localhost)
    uvicorn.run(app, host=API_HOST, port=API_PORT)
