"""
FastAPI Backend for Telecom AI Bot
===================================

This is the main API server that:
- Handles chat conversations
- Processes voice input/output
- Manages language detection
- Connects to Rasa and Sarvam AI

Run: uvicorn backend.main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
import os
import requests
import json
import io
from datetime import datetime
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Telecom AI Bot API",
    description="Multilingual conversational AI for Indian telecom companies",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware - allows frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# CONFIGURATION
# ============================================================================

SARVAM_API_KEY = os.getenv('SARVAM_API_KEY')
SARVAM_BASE_URL = 'https://api.sarvam.ai/v1'
RASA_URL = os.getenv('RASA_URL', 'http://localhost:5005')
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 8000))

SUPPORTED_LANGUAGES = {
    'hi': 'Hindi',
    'ta': 'Tamil',
    'te': 'Telugu',
    'en': 'English',
    'kn': 'Kannada',
    'bn': 'Bengali',
    'mr': 'Marathi'
}

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ChatMessage(BaseModel):
    """Chat message request"""
    text: str = Field(..., description="User message text")
    language: str = Field("en", description="Language code (hi, ta, te, etc)")
    user_id: str = Field("default_user", description="Unique user identifier")
    session_id: Optional[str] = Field(None, description="Conversation session ID")

class ChatResponse(BaseModel):
    """Chat response"""
    bot_response: str
    language: str
    confidence: float = 0.95
    timestamp: str
    session_id: Optional[str] = None
    intent: Optional[str] = None

class LanguageDetectionResponse(BaseModel):
    """Language detection response"""
    detected_language: str
    confidence: float
    text: str

class TranslationRequest(BaseModel):
    """Translation request"""
    text: str
    source_language: str = "en"
    target_language: str = "hi"

class TranslationResponse(BaseModel):
    """Translation response"""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str

class UserProfile(BaseModel):
    """User profile"""
    user_id: str
    phone_number: Optional[str] = None
    name: Optional[str] = None
    preferred_language: str = "en"
    plan: Optional[str] = None
    data_remaining: Optional[float] = None
    balance: Optional[float] = None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_sarvam_headers():
    """Get headers for Sarvam API requests"""
    return {
        'Authorization': f'Bearer {SARVAM_API_KEY}',
        'Content-Type': 'application/json'
    }

def detect_language_simple(text: str) -> str:
    """
    Simple language detection based on keywords
    In production, use Sarvam's language detection API
    """
    hindi_keywords = ['है', 'क्या', 'मेरा', 'करना', 'दें', 'की', 'कर']
    tamil_keywords = ['என்', 'என்ன', 'நான்', 'பயன்', 'இல்', 'எப்']
    telugu_keywords = ['నా', 'ఎంత', 'ఎలా', 'చేయాలి', 'ఉంది', 'ఆ']
    kannada_keywords = ['ನನ್ನ', 'ಯಾವ', 'ಹೇಗೆ', 'ಮಾಡಬೇಕು', 'ಇದೆ']
    bengali_keywords = ['আমার', 'কত', 'কিভাবে', 'করতে', 'আছে']
    marathi_keywords = ['माझा', 'काय', 'कसे', 'करायचे', 'आहे']
    
    text_lower = text.lower()
    
    # Count keyword matches
    scores = {
        'hi': sum(1 for kw in hindi_keywords if kw in text),
        'ta': sum(1 for kw in tamil_keywords if kw in text),
        'te': sum(1 for kw in telugu_keywords if kw in text),
        'kn': sum(1 for kw in kannada_keywords if kw in text),
        'bn': sum(1 for kw in bengali_keywords if kw in text),
        'mr': sum(1 for kw in marathi_keywords if kw in text),
        'en': 0
    }
    
    # Default to English if no matches
    detected = max(scores.items(), key=lambda x: x[1])[0]
    return detected if scores[detected] > 0 else 'en'

def get_mock_rasa_response(user_message: str, language: str):
    """
    Get mock Rasa response
    In production, connect to actual Rasa server
    """
    responses = {
        'hi': {
            'greet': 'नमस्कार! मैं आपकी कैसे मदद कर सकता हूँ?',
            'ask_data_plan': 'आपकी वर्तमान प्लान 30GB मासिक है। आपने 15GB का उपयोग किया है।',
            'ask_recharge': 'आप निम्नलिखित विकल्प चुन सकते हैं: 30GB - ₹399, 50GB - ₹599, 100GB - ₹999',
            'ask_bill': 'आपका इस महीने का बिल ₹499 है।',
            'default': 'मैं आपको समझ नहीं पाया। कृपया दोबारा कहें।'
        },
        'ta': {
            'greet': 'வணக்கம்! நான் உங்களுக்கு எப்படி உதவ முடியும்?',
            'ask_data_plan': 'உங்கள் தற்போதைய திட்டம் மாதத்திற்கு 30GB. நீங்கள் 15GB பயன்படுத்தினீர்கள்.',
            'ask_recharge': 'நீங்கள் தேர்வு செய்யலாம்: 30GB - ₹399, 50GB - ₹599, 100GB - ₹999',
            'ask_bill': 'இந்த மாதத்திற்கு உங்கள் பிலை ₹499.',
            'default': 'என்னை புரிந்துகொள்ள முடியவில்லை. மீண்டும் சொல்லவும்.'
        },
        'te': {
            'greet': 'హలో! నాకు ఎలా సహాయం చేయవచ్చు?',
            'ask_data_plan': 'మీ ప్రస్తుత ప్లాన్ నెలకు 30GB. మీరు 15GB ఉపయోగించారు.',
            'ask_recharge': 'మీరు ఎంచుకోవచ్చు: 30GB - ₹399, 50GB - ₹599, 100GB - ₹999',
            'ask_bill': 'ఈ నెలకు మీ బిల్లు ₹499.',
            'default': 'నన్ను అర్థం చేసుకోలేకపోయాను. మళ్లీ చెప్పండి.'
        },
        'en': {
            'greet': 'Hello! How can I help you today?',
            'ask_data_plan': 'Your current plan is 30GB per month. You have used 15GB.',
            'ask_recharge': 'You can choose: 30GB - ₹399, 50GB - ₹599, 100GB - ₹999',
            'ask_bill': 'Your bill for this month is ₹499.',
            'default': 'I did not understand. Please repeat.'
        }
    }
    
    user_message_lower = user_message.lower()
    lang_responses = responses.get(language, responses['en'])
    
    # Simple intent detection
    if any(word in user_message_lower for word in ['नमस्कार', 'hello', 'hi', 'வணக்கம்', 'హలో']):
        intent = 'greet'
    elif any(word in user_message_lower for word in ['data', 'plan', 'डेटा', 'திட்டம்', 'ప్లాన్']):
        intent = 'ask_data_plan'
    elif any(word in user_message_lower for word in ['recharge', 'रिचार्ज', 'நிரப்ப', 'రీచార్జ్']):
        intent = 'ask_recharge'
    elif any(word in user_message_lower for word in ['bill', 'बिल', 'பிலை', 'బిల్లు']):
        intent = 'ask_bill'
    else:
        intent = 'default'
    
    return {
        'intent': intent,
        'response': lang_responses.get(intent, lang_responses['default'])
    }

# ============================================================================
# ROUTES - HEALTH & INFO
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Telecom AI Bot API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "telecom-ai-bot",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv('ENVIRONMENT', 'production')
    }

@app.get("/config")
async def get_config():
    """Get configuration info"""
    return {
        "supported_languages": SUPPORTED_LANGUAGES,
        "sarvam_available": bool(SARVAM_API_KEY),
        "rasa_url": RASA_URL,
    }

# ============================================================================
# ROUTES - CHAT
# ============================================================================

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Main chat endpoint
    
    Handles:
    - Text input from user
    - Language detection
    - Intent processing via Rasa
    - Response generation
    """
    try:
        # Detect language if not provided
        if message.language == "auto":
            detected_lang = detect_language_simple(message.text)
        else:
            detected_lang = message.language
        
        logger.info(f"Chat request - Text: {message.text[:50]}... Language: {detected_lang}")
        
        # Get response from Rasa (or mock)
        rasa_response = get_mock_rasa_response(message.text, detected_lang)
        
        return ChatResponse(
            bot_response=rasa_response['response'],
            language=detected_lang,
            confidence=0.95,
            timestamp=datetime.now().isoformat(),
            session_id=message.session_id,
            intent=rasa_response['intent']
        )
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ROUTES - LANGUAGE DETECTION
# ============================================================================

@app.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language(text: str):
    """
    Detect language of input text
    
    Supports: Hindi, Tamil, Telugu, English, Kannada, Bengali, Marathi
    """
    try:
        detected = detect_language_simple(text)
        
        logger.info(f"Language detected: {detected} for text: {text[:50]}...")
        
        return LanguageDetectionResponse(
            detected_language=detected,
            confidence=0.85,
            text=text
        )
    
    except Exception as e:
        logger.error(f"Language detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ROUTES - TRANSLATION
# ============================================================================

@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translate text using Sarvam AI
    
    Supports multiple Indian languages
    """
    if not SARVAM_API_KEY:
        raise HTTPException(status_code=400, detail="Sarvam API key not configured")
    
    try:
        headers = get_sarvam_headers()
        
        data = {
            'input': request.text,
            'source_language_code': f'{request.source_language}-IN',
            'target_language_code': f'{request.target_language}-IN',
            'model': 'sarvam-translate:v1'
        }
        
        response = requests.post(
            f'{SARVAM_BASE_URL}/text/translate',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            translated = result.get('translated_text', '')
            
            logger.info(f"Translation: {request.source_language} -> {request.target_language}")
            
            return TranslationResponse(
                original_text=request.text,
                translated_text=translated,
                source_language=request.source_language,
                target_language=request.target_language
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Sarvam API error: {response.text}"
            )
    
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ROUTES - TEXT-TO-SPEECH
# ============================================================================

@app.post("/text-to-speech")
async def text_to_speech(text: str, language: str = "hi"):
    """
    Convert text to speech using Sarvam AI
    
    Returns: Audio file (WAV/MP3)
    """
    if not SARVAM_API_KEY:
        raise HTTPException(status_code=400, detail="Sarvam API key not configured")
    
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Language '{language}' not supported. Supported: {list(SUPPORTED_LANGUAGES.keys())}"
        )
    
    try:
        headers = get_sarvam_headers()
        
        data = {
            'text': text,
            'language_code': f'{language}-IN',
            'model': 'sarvam-tts:v1'
        }
        
        response = requests.post(
            f'{SARVAM_BASE_URL}/text-to-speech',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"Generated speech for: {text[:50]}... Language: {language}")
            
            return StreamingResponse(
                iter([response.content]),
                media_type="audio/wav",
                headers={
                    "Content-Disposition": f"attachment; filename=audio_{language}.wav"
                }
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Sarvam API error: {response.text}"
            )
    
    except Exception as e:
        logger.error(f"Text-to-Speech error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ROUTES - SPEECH-TO-TEXT
# ============================================================================

@app.post("/speech-to-text")
async def speech_to_text(file: UploadFile = File(...), language: str = Form("hi")):
    """
    Convert speech to text using Sarvam AI
    
    Accepts: WAV, MP3, FLAC files
    Returns: Transcribed text
    """
    if not SARVAM_API_KEY:
        raise HTTPException(status_code=400, detail="Sarvam API key not configured")
    
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Language '{language}' not supported"
        )
    
    try:
        # Read uploaded file
        audio_content = await file.read()
        
        headers = {
            'Authorization': f'Bearer {SARVAM_API_KEY}'
        }
        
        files = {
            'audio': (file.filename, audio_content, file.content_type)
        }
        
        params = {
            'language_code': f'{language}-IN'
        }
        
        response = requests.post(
            f'{SARVAM_BASE_URL}/speech-to-text',
            headers=headers,
            files=files,
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            transcript = result.get('transcript', '')
            
            logger.info(f"Transcribed: {transcript[:50]}... Language: {language}")
            
            return {
                "text": transcript,
                "language": language,
                "confidence": result.get('confidence', 0.9),
                "duration": result.get('duration', 0)
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Sarvam API error: {response.text}"
            )
    
    except Exception as e:
        logger.error(f"Speech-to-Text error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ROUTES - USER PROFILE
# ============================================================================

@app.get("/user/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """
    Get user profile
    
    In production, fetch from database
    """
    # Mock user data
    mock_users = {
        "user_123": {
            "user_id": "user_123",
            "phone_number": "9876543210",
            "name": "Rajesh Kumar",
            "preferred_language": "hi",
            "plan": "30GB",
            "data_remaining": 15.0,
            "balance": 499.50
        }
    }
    
    user = mock_users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfile(**user)

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP Exception: {exc.detail}")
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    logger.info("=" * 60)
    logger.info("Telecom AI Bot API Starting")
    logger.info(f"Sarvam API Available: {bool(SARVAM_API_KEY)}")
    logger.info(f"Supported Languages: {list(SUPPORTED_LANGUAGES.keys())}")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    logger.info("Telecom AI Bot API Shutting Down")

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level="info"
    )
