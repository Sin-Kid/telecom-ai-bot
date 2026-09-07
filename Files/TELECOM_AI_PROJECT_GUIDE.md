# Multilingual Conversational AI for Indian Telecom Ecosystems
## Complete Step-by-Step Build Guide

---

## **PROJECT OVERVIEW**

Build a voice-enabled, multilingual chatbot that handles customer service for Indian telecom companies across Hindi, Tamil, Telugu, Kannada, and English.

### **Architecture**
```
User (Voice/Text)
    ↓
Frontend (Phone Interface)
    ↓
Backend API (FastAPI)
    ↓
NLU Layer (Rasa)
    ↓
LLM Layer (Sarvam-M)
    ↓
Voice Processing (Sarvam APIs)
    ↓
Database (Simple JSON/SQLite)
```

---

## **PHASE 1: ENVIRONMENT SETUP (Days 1-2)**

### **Step 1.1: Install Prerequisites**

**You need:**
- Python 3.8+ (https://www.python.org/downloads/)
- Git (https://git-scm.com/download)
- Visual Studio Code (optional but recommended)

**Verify installation:**
```bash
python --version
git --version
```

### **Step 1.2: Create Project Structure**

```bash
mkdir telecom-ai-bot
cd telecom-ai-bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Create folder structure
mkdir backend
mkdir frontend
mkdir data
mkdir models
mkdir notebooks
```

### **Step 1.3: Create requirements.txt**

Save this as `requirements.txt` in project root:

```
# Core
python-dotenv==1.0.0
requests==2.31.0

# Backend API
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-multipart==0.0.6

# NLU & ML
rasa==3.5.0
rasa-sdk==3.5.0
sklearn-crfsuite==0.6.1

# Sarvam AI Integration
sarvam==0.1.0

# Database
sqlite3  # Built-in

# Utils
numpy==1.24.3
pandas==1.5.3
pyyaml==6.0
```

### **Step 1.4: Install Dependencies**

```bash
pip install -r requirements.txt
```

This will take 5-10 minutes. Go grab coffee! ☕

---

## **PHASE 2: SETUP SARVAM AI (Days 2-3)**

### **Step 2.1: Create Sarvam Account**

1. Go to https://www.sarvam.ai/
2. Sign up (free account)
3. Apply for startup programme (free ₹1,000 credits)
4. Get your API key from dashboard

### **Step 2.2: Create .env File**

Create `.env` in project root:

```env
# Sarvam AI Credentials
SARVAM_API_KEY=your_api_key_here

# App Settings
ENVIRONMENT=development
DEBUG=True

# Supported Languages
LANGUAGES=hi,ta,te,en,kn

# Database
DATABASE_PATH=./data/telecom_bot.db
```

### **Step 2.3: Test Sarvam API Connection**

Create `test_sarvam_connection.py`:

```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv('SARVAM_API_KEY')
SARVAM_BASE_URL = 'https://api.sarvam.ai/v1'

def test_speech_to_text():
    """Test speech-to-text API"""
    print("Testing Speech-to-Text...")
    # This requires an audio file
    # For now, just verify connection
    headers = {'Authorization': f'Bearer {SARVAM_API_KEY}'}
    response = requests.get(f'{SARVAM_BASE_URL}/models', headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Available models: {response.json()}")

def test_text_to_speech():
    """Test text-to-speech API"""
    print("\nTesting Text-to-Speech...")
    headers = {'Authorization': f'Bearer {SARVAM_API_KEY}'}
    data = {
        'text': 'नमस्कार, यह एक परीक्षण है',
        'language_code': 'hi-IN',
        'model': 'sarvam-tts:v1'
    }
    response = requests.post(
        f'{SARVAM_BASE_URL}/text-to-speech',
        headers=headers,
        json=data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Text-to-Speech working!")
    else:
        print(f"Error: {response.text}")

def test_translation():
    """Test translation API"""
    print("\nTesting Translation...")
    headers = {'Authorization': f'Bearer {SARVAM_API_KEY}'}
    data = {
        'input': 'My current data plan is 30GB',
        'source_language_code': 'en-IN',
        'target_language_code': 'hi-IN',
        'model': 'sarvam-translate:v1'
    }
    response = requests.post(
        f'{SARVAM_BASE_URL}/text/translate',
        headers=headers,
        json=data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Translation: {result}")
    else:
        print(f"Error: {response.text}")

if __name__ == '__main__':
    if not SARVAM_API_KEY:
        print("❌ SARVAM_API_KEY not set in .env file")
        exit(1)
    
    print("Testing Sarvam AI APIs...\n")
    test_speech_to_text()
    test_text_to_speech()
    test_translation()
    print("\n✓ All tests complete!")
```

Run it:
```bash
python test_sarvam_connection.py
```

---

## **PHASE 3: BUILD NLU WITH RASA (Days 3-5)**

### **Step 3.1: Initialize Rasa Project**

```bash
cd backend
rasa init --no-prompt
cd ..
```

This creates a basic Rasa project structure.

### **Step 3.2: Define Intents**

Create `backend/data/nlu.yml`:

```yaml
version: "3.1"
nlu:

# Greeting intents
- intent: greet
  examples: |
    - नमस्कार
    - आपका स्वागत है
    - हलो
    - हाय
    - வணக்கம்
    - தமிழ் வணக்கம்
    - హలో
    - నమస్కారం
    - hello
    - hi
    - hey

# Plan inquiry intents
- intent: ask_data_plan
  examples: |
    - मेरी डेटा प्लान क्या है
    - मेरे पास कितना डेटा बचा है
    - डेटा प्लान की जानकारी दे
    - எனது டேटா திட்டம் என்ன
    - ডেটা பরিকল্পনা সম্পর্কে তথ্য
    - నా డేటా ప్లాన్ ఏమిటి
    - what is my data plan
    - how much data do I have
    - my current plan

# Recharge intent
- intent: ask_recharge
  examples: |
    - रिचार्ज कैसे करें
    - मुझे रिचार्ज करना है
    - रिचार्ज विकल्प बताएं
    - எனது பயன் மீட்டர் நிரப்பவேண்டும்
    - রিচার্জ কীভাবে করতে হয়
    - నా ఖాతాను రీచార్జ్ చేయండి
    - how to recharge
    - I need recharge

# Billing intent
- intent: ask_bill
  examples: |
    - मेरा बिल क्या है
    - बिल की जानकारी दें
    - महीने का खर्च कितना है
    - என் பிலை என்ன
    - আমার বিল কত
    - నా బిల్లు ఎంత
    - what is my bill
    - show my bill

# Complaint intent
- intent: lodge_complaint
  examples: |
    - नेटवर्क खराब है
    - कॉल कट हो रहे हैं
    - शिकायत दर्ज करनी है
    - எனது நெட்வொர்க் மிகவும் மெதுவாக உள்ளது
    - আমার সিগন্যাল কম है
    - నా నెట్‌వర్క్ తీవ్రంగా ఉంది
    - network is bad
    - poor signal
    - I have a complaint

# Support intent
- intent: talk_to_support
  examples: |
    - मुझे सपोर्ट से बात करनी है
    - कस्टमर केयर से जुड़ें
    - मानव सहायता चाहिए
    - நான் ஒரு ஏஜெண்ட் பேச விரும்புகிறேன்
    - একজন মানুষের সাথে কথা বলুন
    - నేను ఏజెంట్‌తో మాట్లాడాలనుకుంటున్నాను
    - talk to a human
    - human support

# Goodbye intent
- intent: goodbye
  examples: |
    - धन्यवाद, बाय
    - अलविदा
    - फिर मिलेंगे
    - விடைபெறுகிறேன்
    - বিদায়
    - తిరిగిస్తాను
    - goodbye
    - bye
    - see you

# Affirm/Deny
- intent: affirm
  examples: |
    - हाँ
    - जी
    - सही है
    - ठीक है
    - ஆம்
    - হ্যাঁ
    - అవును
    - yes
    - okay
    - correct

- intent: deny
  examples: |
    - नहीं
    - मत करो
    - बिलकुल नहीं
    - இல்லை
    - না
    - కాదు
    - no
    - nope
    - not really

# Entities
- intent: inform
  examples: |
    - मेरा नाम [name](name) है
    - मेरा नंबर [9876543210](phone) है
    - मेरा आईडी [MTN123](customer_id) है
    - என் பெயர் [Rajesh](name)
    - আমার ফোন [9876543210](phone)
    - నా ID [ABC123](customer_id)

```

### **Step 3.3: Define Stories (Dialogue Flows)**

Create `backend/data/stories.yml`:

```yaml
version: "3.1"
stories:

- story: greet and ask data plan
  steps:
  - intent: greet
  - action: action_greet
  - intent: ask_data_plan
  - action: action_fetch_data_plan
  - intent: affirm
  - action: action_offer_upgrade

- story: ask recharge
  steps:
  - intent: ask_recharge
  - action: action_recharge_options

- story: lodge complaint
  steps:
  - intent: lodge_complaint
  - action: action_lodge_complaint
  - intent: affirm
  - action: action_complaint_confirmation

- story: talk to support
  steps:
  - intent: talk_to_support
  - action: action_escalate_to_human

- story: goodbye
  steps:
  - intent: goodbye
  - action: action_goodbye
```

### **Step 3.4: Define Domain**

Create `backend/data/domain.yml`:

```yaml
version: "3.1"
intents:
  - greet
  - ask_data_plan
  - ask_recharge
  - ask_bill
  - lodge_complaint
  - talk_to_support
  - goodbye
  - affirm
  - deny
  - inform

entities:
  - name
  - phone
  - customer_id

slots:
  customer_name:
    type: text
  customer_phone:
    type: text
  customer_id:
    type: text
  data_remaining:
    type: float
  current_plan:
    type: text

responses:
  utter_greet:
    - text: "नमस्कार! मैं आपकी कैसे मदद कर सकता हूँ?"
    - text: "வணக்கம்! நான் உங்களுக்கு எப்படி உதவ முடியும்?"
    - text: "హలో! నాకు ఎలా సహాయం చేయవచ్చు?"
  
  utter_goodbye:
    - text: "धन्यवाद! फिर मिलेंगे।"
    - text: "நன்றி! மீண்டும் சந்திப்போம்."
    - text: "ధన్యవాదాలు! మళ్ళీ కలుద్దాం."

actions:
  - action_greet
  - action_fetch_data_plan
  - action_offer_upgrade
  - action_recharge_options
  - action_lodge_complaint
  - action_complaint_confirmation
  - action_escalate_to_human
  - action_goodbye
```

---

## **PHASE 4: CREATE CUSTOM ACTIONS (Days 5-6)**

Create `backend/actions/actions.py`:

```python
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv('SARVAM_API_KEY')
SARVAM_BASE_URL = 'https://api.sarvam.ai/v1'

class ActionGreet(Action):
    def name(self):
        return "action_greet"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        language = tracker.get_slot("language") or "hi"
        
        greetings = {
            "hi": "नमस्कार! मैं आपकी कैसे मदद कर सकता हूँ?",
            "ta": "வணக்கம்! நான் உங்களுக்கு எப்படி உதவ முடியும்?",
            "te": "హలో! నాకు ఎలా సహాయం చేయవచ్చు?",
            "en": "Hello! How can I help you today?"
        }
        
        dispatcher.utter_message(text=greetings.get(language, greetings["en"]))
        return []

class ActionFetchDataPlan(Action):
    def name(self):
        return "action_fetch_data_plan"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Simulated customer data - in real scenario, fetch from database
        customer_data = {
            "plan": "30GB",
            "used": "15GB",
            "remaining": "15GB",
            "validity": "28 days"
        }
        
        language = tracker.get_slot("language") or "hi"
        
        messages = {
            "hi": f"आपकी वर्तमान प्लान {customer_data['plan']} मासिक है। आपने {customer_data['used']} का उपयोग किया है। {customer_data['remaining']} बचा है।",
            "ta": f"உங்கள் தற்போதைய திட்டம் மாதத்திற்கு {customer_data['plan']}. நீங்கள் {customer_data['used']} பயன்படுத்தினீர்கள். {customer_data['remaining']} மீதமுள்ளது.",
            "te": f"మీ ప్రస్తుత ప్లాన్ నెలకు {customer_data['plan']}. మీరు {customer_data['used']} ఉపయోగించారు. {customer_data['remaining']} మిగిలి ఉంది.",
            "en": f"Your current plan is {customer_data['plan']} per month. You've used {customer_data['used']}. {customer_data['remaining']} remaining."
        }
        
        dispatcher.utter_message(text=messages.get(language, messages["en"]))
        
        return [
            SlotSet("current_plan", customer_data['plan']),
            SlotSet("data_remaining", customer_data['remaining'])
        ]

class ActionRechargeOptions(Action):
    def name(self):
        return "action_recharge_options"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        language = tracker.get_slot("language") or "hi"
        
        options = {
            "hi": "आप निम्नलिखित विकल्प चुन सकते हैं:\n1. 30GB - ₹399\n2. 50GB - ₹599\n3. 100GB - ₹999\n\nकौन सा चुनना चाहते हैं?",
            "ta": "நீங்கள் பின்வரும் விருப்பங்களைத் தேர்வு செய்யலாம்:\n1. 30GB - ₹399\n2. 50GB - ₹599\n3. 100GB - ₹999",
            "te": "మీరు క్రింది ఎంపికలను ఎంచుకోవచ్చు:\n1. 30GB - ₹399\n2. 50GB - ₹599\n3. 100GB - ₹999",
            "en": "You can choose from:\n1. 30GB - ₹399\n2. 50GB - ₹599\n3. 100GB - ₹999"
        }
        
        dispatcher.utter_message(text=options.get(language, options["en"]))
        return []

class ActionLodgeComplaint(Action):
    def name(self):
        return "action_lodge_complaint"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        language = tracker.get_slot("language") or "hi"
        
        messages = {
            "hi": "मुझे खेद है कि आप समस्या का सामना कर रहे हैं। मैं आपकी शिकायत दर्ज करता हूँ। एक टिकट नंबर जेनरेट किया गया है: TKT-2024-001",
            "ta": "நீங்கள் சிக்கலை எதிர்கொள்வதற்கு வருந்துகிறேன். உங்கள் புகாரை பதிவு செய்கிறேன்.",
            "te": "మీరు సమస్యను ఎదుర్కొంటున్నందుకు క్షమించండి. మీ ఫిర్యాదు నమోదు చేస్తున్నాను.",
            "en": "I'm sorry to hear you're experiencing issues. I'm logging your complaint. Ticket: TKT-2024-001"
        }
        
        dispatcher.utter_message(text=messages.get(language, messages["en"]))
        return []

class ActionEscalateToHuman(Action):
    def name(self):
        return "action_escalate_to_human"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        language = tracker.get_slot("language") or "hi"
        
        messages = {
            "hi": "मैं आपको एक मानव एजेंट से जोड़ता हूँ। कृपया प्रतीक्षा करें...",
            "ta": "உங்களை ஒரு மানிட முகவரிடம் இணைக்கிறேன்.",
            "te": "నిన్ను ఒక మానవ ఏజెంట్‌కు కనెక్ట్ చేస్తున్నాను.",
            "en": "Connecting you to a human agent..."
        }
        
        dispatcher.utter_message(text=messages.get(language, messages["en"]))
        return []

class ActionGoodbye(Action):
    def name(self):
        return "action_goodbye"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        language = tracker.get_slot("language") or "hi"
        
        messages = {
            "hi": "धन्यवाद! अगर कोई और सहायता चाहिए तो बेझिझक कॉल करें। अलविदा!",
            "ta": "நன்றி! மீண்டும் சந்திப்போம்.",
            "te": "ధన్యవాదాలు! మళ్ళీ కలుద్దాం.",
            "en": "Thank you! Goodbye and have a great day!"
        }
        
        dispatcher.utter_message(text=messages.get(language, messages["en"]))
        return []
```

---

## **PHASE 5: BUILD FASTAPI BACKEND (Days 6-7)**

Create `backend/main.py`:

```python
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

app = FastAPI(
    title="Telecom AI Bot",
    description="Multilingual conversational AI for Indian telecom",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SARVAM_API_KEY = os.getenv('SARVAM_API_KEY')
SARVAM_BASE_URL = 'https://api.sarvam.ai/v1'

# Request/Response Models
class ChatMessage(BaseModel):
    text: str
    language: str = "hi"
    user_id: str = "default"

class ChatResponse(BaseModel):
    bot_response: str
    language: str
    confidence: float = 0.95

class VoiceInput(BaseModel):
    language: str = "hi"

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "telecom-ai-bot"}

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    try:
        # Process with Rasa
        # For now, return simple response
        
        responses = {
            "hi": "नमस्कार! आपकी कैसे मदद कर सकता हूँ?",
            "ta": "வணக்கம்! நான் உங்களுக்கு எப்படி உதவ முடியும்?",
            "te": "హలో! నాకు ఎలా సహాయం చేయవచ్చు?",
            "en": "Hello! How can I help you?"
        }
        
        return ChatResponse(
            bot_response=responses.get(message.language, responses["en"]),
            language=message.language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Speech-to-text endpoint
@app.post("/speech-to-text")
async def speech_to_text(file: UploadFile = File(...), language: str = "hi"):
    try:
        # Read audio file
        audio_content = await file.read()
        
        # Call Sarvam API
        headers = {'Authorization': f'Bearer {SARVAM_API_KEY}'}
        files = {'audio': audio_content}
        params = {'language_code': f'{language}-IN'}
        
        response = requests.post(
            f'{SARVAM_BASE_URL}/speech-to-text',
            headers=headers,
            files=files,
            params=params
        )
        
        if response.status_code == 200:
            result = response.json()
            return {"text": result.get('transcript', ''), "language": language}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Text-to-speech endpoint
@app.post("/text-to-speech")
async def text_to_speech(text: str, language: str = "hi"):
    try:
        headers = {'Authorization': f'Bearer {SARVAM_API_KEY}'}
        data = {
            'text': text,
            'language_code': f'{language}-IN',
            'model': 'sarvam-tts:v1'
        }
        
        response = requests.post(
            f'{SARVAM_BASE_URL}/text-to-speech',
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.content  # Return audio bytes
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Language detection endpoint
@app.post("/detect-language")
async def detect_language(text: str):
    try:
        # Simple language detection based on keywords
        hindi_keywords = ['है', 'क्या', 'मेरा', 'करना', 'दें']
        tamil_keywords = ['என்', 'என்ன', 'என்', 'பயன்']
        telugu_keywords = ['నా', 'ఎంత', 'ఎలా', 'చేయాలి']
        
        detected_lang = "en"
        if any(keyword in text for keyword in hindi_keywords):
            detected_lang = "hi"
        elif any(keyword in text for keyword in tamil_keywords):
            detected_lang = "ta"
        elif any(keyword in text for keyword in telugu_keywords):
            detected_lang = "te"
        
        return {"detected_language": detected_lang, "text": text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## **PHASE 6: FRONTEND - PHONE INTERFACE (Days 7-8)**

Create `frontend/index.html` (see phone interface widget from previous response)

---

## **PHASE 7: DATABASE SETUP (Day 8)**

Create `backend/database.py`:

```python
import sqlite3
import os
from datetime import datetime

DB_PATH = os.getenv('DATABASE_PATH', './data/telecom_bot.db')

def init_database():
    """Initialize database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            phone_number TEXT UNIQUE,
            name TEXT,
            language TEXT DEFAULT 'hi',
            current_plan TEXT,
            data_remaining FLOAT,
            balance FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            user_message TEXT,
            bot_response TEXT,
            language TEXT,
            intent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            issue_type TEXT,
            description TEXT,
            status TEXT DEFAULT 'open',
            ticket_number TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Database initialized!")

if __name__ == '__main__':
    init_database()
```

---

## **RUNNING THE PROJECT**

### **Terminal 1: Start Backend**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

You'll see: `Uvicorn running on http://127.0.0.1:8000`

### **Terminal 2: Train Rasa**
```bash
cd backend
rasa train
```

### **Terminal 3: Start Frontend**
```bash
cd frontend
# If using Python HTTP server
python -m http.server 5000
```

Then open: http://localhost:5000

---

## **TESTING CHECKLIST**

✓ Python environment activated
✓ Dependencies installed
✓ .env file created with SARVAM_API_KEY
✓ Sarvam connection test passes
✓ Rasa NLU trained
✓ Backend API running
✓ Frontend loads
✓ Chat works end-to-end

---

## **NEXT STEPS**

1. Add real audio input/output
2. Integrate Rasa with FastAPI
3. Add database persistence
4. Deploy to cloud (Hugging Face Spaces)
5. Add more telecom scenarios
6. Implement analytics/logging

---

**Good luck! Let's build this step-by-step together! 🚀**
