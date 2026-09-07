"""
Local TTS Engine with Multi-Language Support
Supports Kannada (kn) and English/Hindi (en/hi)
"""

import os
import sys
import io
import base64
import logging
import torch

# Ensure the local TTS folder is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "TTS")))

try:
    from TTS.utils.synthesizer import Synthesizer
except ImportError:
    Synthesizer = None

logger = logging.getLogger(__name__)

# Base path for models
MODEL_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "indic-tts"))

# Model Configurations
MODELS_CONFIG = {
    "kn": {
        "model":  "/Users/pavang/Documents/DSA-EL/models/indic-tts/kannada/fastpitch/best_model.pth",
        "config": "/Users/pavang/Documents/DSA-EL/models/indic-tts/kannada/fastpitch/config.json",
        "vocoder": "/Users/pavang/Documents/DSA-EL/models/indic-tts/kannada/hifigan/best_model.pth",
        "vocoder_config": "/Users/pavang/Documents/DSA-EL/models/indic-tts/kannada/hifigan/config.json",
    },
    "hi": {
        "model":  "/Users/pavang/Documents/DSA-EL/models/indic-tts/hindi/fastpitch/best_model.pth",
        "config": "/Users/pavang/Documents/DSA-EL/models/indic-tts/hindi/fastpitch/config.json",
        "vocoder": "/Users/pavang/Documents/DSA-EL/models/indic-tts/hindi/hifigan/best_model.pth",
        "vocoder_config": "/Users/pavang/Documents/DSA-EL/models/indic-tts/hindi/hifigan/config.json",
    },
    "en": {
        "model":  "/Users/pavang/Documents/DSA-EL/models/indic-tts/english+hindi/fastpitch/best_model.pth",
        "config": "/Users/pavang/Documents/DSA-EL/models/indic-tts/english+hindi/fastpitch/config.json",
        "vocoder": "/Users/pavang/Documents/DSA-EL/models/indic-tts/english+hindi/hifigan/best_model.pth",
        "vocoder_config": "/Users/pavang/Documents/DSA-EL/models/indic-tts/english+hindi/hifigan/config.json",
    },
    "te": {
        "model":  "/Users/pavang/Documents/DSA-EL/models/indic-tts/telugu/fastpitch/best_model.pth",
        "config": "/Users/pavang/Documents/DSA-EL/models/indic-tts/telugu/fastpitch/config.json",
        "vocoder": "/Users/pavang/Documents/DSA-EL/models/indic-tts/telugu/hifigan/best_model.pth",
        "vocoder_config": "/Users/pavang/Documents/DSA-EL/models/indic-tts/telugu/hifigan/config.json",
    }
}

# ── Voice Settings ─────────────────────────────────────────────────────────
# Change these names to switch the AI voice:
# English options:      'female', 'male', 'hindifemale', 'hindimale'
# Kannada options:      'female', 'male'
# Hindi options:        'female', 'male'
# Telugu options:       'female', 'male'
DEFAULT_SPEAKERS = {
    "kn": "female",
    "en": "hindifemale", # hindifemale is much clearer and natural for Indian-accented English
    "hi": "female",
    "te": "female"
}

# ── Text Normalizer ────────────────────────────────────────────────────────

import re
import html
try:
    from num2words import num2words
except ImportError:
    num2words = None

HINDI_NUMBERS = {
    0: "शून्य", 1: "एक", 1.5: "एक दशमलव पांच", 2: "दो", 1.2: "एक दशमलव दो", 
    0.3: "शून्य दशमलव तीन", 0.5: "शून्य दशमलव पांच", 0.7: "शून्य दशमलव सात",
    0.8: "शून्य दशमलव आठ", 1.8: "एक दशमलव आठ", 28: "अट्ठाईस", 56: "छप्पन", 
    84: "चौरासी", 50: "पचास", 75: "पचहत्तर", 120.5: "एक सौ बीस दशमलव पांच",
    197: "एक सौ सत्तानवे", 230: "दो सौ तीस", 249: "दो सौ उनचास", 
    299: "दो सौ निन्यानवे", 359: "तीन सौ उनसठ", 399: "तीन सौ निन्यानवे", 
    449: "चार सौ उनचास", 450: "चार सौ पचास", 479: "चार सौ उनासी", 
    599: "पांच सौ निन्यानवे", 719: "सात सौ उन्नीस", 999: "नौ सौ निन्यानवे"
}
HINDI_DIGITS = {
    '0': 'शून्य', '1': 'एक', '2': 'दो', '3': 'तीन', '4': 'चार', 
    '5': 'पाँच', '6': 'छह', '7': 'सात', '8': 'आठ', '9': 'नौ'
}

def convert_number_to_words(text_match, language: str) -> str:
    val_str = text_match.group(0)
    try:
        val = float(val_str)
        if val.is_integer():
            val = int(val)
    except ValueError:
        return val_str

    if language == "en":
        if num2words:
            return " " + num2words(val, lang="en_IN").replace("-", " ") + " "
        return " " + val_str + " "
    elif language == "kn":
        if num2words:
            return " " + num2words(val, lang="kn") + " "
        return " " + val_str + " "
    elif language == "te":
        if num2words:
            return " " + num2words(val, lang="te") + " "
        return " " + val_str + " "
    elif language == "hi":
        if val in HINDI_NUMBERS:
            return " " + HINDI_NUMBERS[val] + " "
        # Digit by digit fallback
        return " " + " ".join(HINDI_DIGITS.get(d, d) for d in str(val).replace(".", " दशमलव ")) + " "
    
    return " " + val_str + " "

def normalize_text(text: str, language: str) -> str:
    # 1. Clean HTML and markdown
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)  # remove HTML tags like <i>, 📡, etc.
    text = re.sub(r"[\*\_`~\[\]\(\)#\-\+]", "", text)  # remove markdown symbols
    
    # Remove emoji & symbols
    text = re.sub(r'[^\w\s\.\,₹\/%]', '', text)

    # 2. Handle specific unit & symbol transformations
    if language == "en":
        text = text.replace("₹", " rupees ")
        text = text.replace("/", " per ")
        text = text.replace("%", " percent ")
        # Separate letters of abbreviations so TTS spells them properly
        text = re.sub(r"\bGB\b", " G B ", text)
        text = re.sub(r"\bMB\b", " M B ", text)
        text = re.sub(r"\bVi\b", " V I ", text)
        text = re.sub(r"\bBSNL\b", " B S N L ", text)
        text = re.sub(r"\bISD\b", " I S D ", text)
    elif language == "kn":
        text = text.replace("₹", " ರೂಪಾಯಿ ")
        text = text.replace("/", " ಪ್ರತಿ ")
        text = text.replace("%", " ಶೇಕಡಾ ")
        # Convert English terms to Kannada script
        text = re.sub(r"\bTeleBot\b", " ಟೆಲಿಬಾಟ್ ", text, flags=re.I)
        text = re.sub(r"\bAI\b", " ಏಐ ", text, flags=re.I)
        text = re.sub(r"\bGB\b", " ಜಿಬಿ ", text, flags=re.I)
        text = re.sub(r"\bMB\b", " ಎಂಬಿ ", text, flags=re.I)
        text = re.sub(r"\bAirtel\b", " ಏರ್ಟೆಲ್ ", text, flags=re.I)
        text = re.sub(r"\bJio\b", " ಜಿಯೋ ", text, flags=re.I)
        text = re.sub(r"\bVi\b", " ವಿ ", text, flags=re.I)
        text = re.sub(r"\bBSNL\b", " ಬಿಎಸ್ಎನ್ಎಲ್ ", text, flags=re.I)
        text = re.sub(r"\bunlimited\b", " ಅನ್ಲಿಮಿಟೆಡ್ ", text, flags=re.I)
        text = re.sub(r"\bcalls\b", " ಕರೆಗಳು ", text, flags=re.I)
        text = re.sub(r"\bplan\b", " ಪ್ಲಾನ್ ", text, flags=re.I)
        text = re.sub(r"\bdata\b", " ಡೇಟಾ ", text, flags=re.I)
        text = re.sub(r"\bbalance\b", " ಬ್ಯಾಲೆನ್ಸ್ ", text, flags=re.I)
        text = re.sub(r"\binternet\b", " ಇಂಟರ್ನೆಟ್ ", text, flags=re.I)
        text = re.sub(r"\bsim\b", " ಸಿಮ್ ", text, flags=re.I)
        text = re.sub(r"\bsms\b", " ಎಸ್ಎಮ್ಎಸ್ ", text, flags=re.I)
    elif language == "te":
        text = text.replace("₹", " రూపాయలు ")
        text = text.replace("/", " ప్రతి ")
        text = text.replace("%", " శాతం ")
        # Convert English terms to Telugu script
        text = re.sub(r"\bTeleBot\b", " టెలిబాట్ ", text, flags=re.I)
        text = re.sub(r"\bAI\b", " ఏఐ ", text, flags=re.I)
        text = re.sub(r"\bGB\b", " జీబీ ", text, flags=re.I)
        text = re.sub(r"\bMB\b", " ఎంబీ ", text, flags=re.I)
        text = re.sub(r"\bAirtel\b", " ఎయిర్టెల్ ", text, flags=re.I)
        text = re.sub(r"\bJio\b", " జియో ", text, flags=re.I)
        text = re.sub(r"\bVi\b", " వి ", text, flags=re.I)
        text = re.sub(r"\bBSNL\b", " బిఎస్ఎన్ఎల్ ", text, flags=re.I)
        text = re.sub(r"\bunlimited\b", " అన్లిమిటెడ్ ", text, flags=re.I)
        text = re.sub(r"\bcalls\b", " కాల్స్ ", text, flags=re.I)
        text = re.sub(r"\bplan\b", " ప్లాన్ ", text, flags=re.I)
        text = re.sub(r"\bdata\b", " డేటా ", text, flags=re.I)
        text = re.sub(r"\bbalance\b", " బ్యాలెన్స్ ", text, flags=re.I)
        text = re.sub(r"\binternet\b", " ఇంటర్నెట్ ", text, flags=re.I)
        text = re.sub(r"\bsim\b", " సిమ్ ", text, flags=re.I)
        text = re.sub(r"\bsms\b", " ఎస్ఎంఎస్ ", text, flags=re.I)
    elif language == "hi":
        text = text.replace("₹", " रुपये ")
        text = text.replace("/", " प्रति ")
        text = text.replace("%", " प्रतिशत ")
        # Convert English terms to Hindi script
        text = re.sub(r"\bTeleBot\b", " टेलीबॉट ", text, flags=re.I)
        text = re.sub(r"\bAI\b", " एआई ", text, flags=re.I)
        text = re.sub(r"\bGB\b", " जीबी ", text, flags=re.I)
        text = re.sub(r"\bMB\b", " एमबी ", text, flags=re.I)
        text = re.sub(r"\bAirtel\b", " एयरटेल ", text, flags=re.I)
        text = re.sub(r"\bJio\b", " जियो ", text, flags=re.I)
        text = re.sub(r"\bVi\b", " वी ", text, flags=re.I)
        text = re.sub(r"\bBSNL\b", " बीएसएनएल ", text, flags=re.I)
        text = re.sub(r"\bunlimited\b", " अनलिमिटेड ", text, flags=re.I)
        text = re.sub(r"\bcalls\b", " कॉल्स ", text, flags=re.I)
        text = re.sub(r"\bplan\b", " प्लान ", text, flags=re.I)
        text = re.sub(r"\bdata\b", " डेटा ", text, flags=re.I)
        text = re.sub(r"\bbalance\b", " बैलेंस ", text, flags=re.I)
        text = re.sub(r"\binternet\b", " इंटरनेट ", text, flags=re.I)
        text = re.sub(r"\bsim\b", " सिम ", text, flags=re.I)
        text = re.sub(r"\bsms\b", " एसएमएस ", text, flags=re.I)

    # 3. Normalize all numbers into words
    text = re.sub(r"\b\d+(?:\.\d+)?\b", lambda m: convert_number_to_words(m, language), text)

    # Clean double spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text
# ──────────────────────────────────────────────────────────────────────────

class IndicTTSEngine:
    def __init__(self):
        self.synthesizers = {}

    def _load_model_for_lang(self, lang: str):
        """Lazily load the Synthesizer model for a specific language if not already loaded."""
        if Synthesizer is None:
            logger.error("❌ TTS library not found in path.")
            return None

        if lang in self.synthesizers:
            return self.synthesizers[lang]

        paths = MODELS_CONFIG.get(lang)
        if not paths:
            logger.error(f"❌ No model config found for language: {lang}")
            return None

        try:
            logger.info(f"🔄 [Lazy Load] Loading Local Indic-TTS for {lang}...")
            self.synthesizers[lang] = Synthesizer(
                tts_checkpoint=paths["model"],
                tts_config_path=paths["config"],
                vocoder_checkpoint=paths["vocoder"],
                vocoder_config=paths["vocoder_config"],
                use_cuda=torch.cuda.is_available()
            )
            logger.info(f"✅ [Lazy Load] {lang} model loaded successfully.")
            return self.synthesizers[lang]
        except Exception as e:
            logger.error(f"❌ Failed to load {lang} model: {e}")
            return None

    @property
    def is_ready(self):
        # We are ready if the TTS package is imported and we can load models dynamically
        return Synthesizer is not None

    def generate_voice(self, text: str, language: str = "kn") -> str | None:
        if not self.is_ready:
            return None

        # Dynamically load the requested model if it's not already loaded
        synth = self._load_model_for_lang(language)
        if not synth:
            return None

        try:
            # Preprocess and normalize text for clean synthesis (replace numbers, symbols, abbreviations)
            clean_text = normalize_text(text, language)
            logger.info(f"🔊 Synthesizing [{language}]: '{text[:40]}' -> Normalized: '{clean_text[:50]}'")

            # Use the configured speaker for the language
            speaker = DEFAULT_SPEAKERS.get(language, "female")
            wav = synth.tts(clean_text, speaker_name=speaker)
            
            if wav is None or len(wav) == 0:
                return None

            import io
            import base64
            import soundfile as sf
            
            buffer = io.BytesIO()
            sf.write(buffer, wav, 22050, format="WAV")
            buffer.seek(0)
            return base64.b64encode(buffer.read()).decode("utf-8")

        except Exception as e:
            # This catches the "Dimension out of range" error if the text is all non-vocab chars
            logger.warning(f"TTS skipped for text: '{text[:20]}...' (Likely vocabulary mismatch)")
            return None


# ── Singleton ──────────────────────────────────────────────────────────────
_engine_instance: IndicTTSEngine | None = None

def get_engine() -> IndicTTSEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = IndicTTSEngine()
    return _engine_instance
