# Quick Start Guide - Telecom AI Bot
## Get Everything Running in 30 Minutes ⚡

---

## **BEFORE YOU START**

You need:
- Python 3.8+ installed ([Download](https://www.python.org/downloads/))
- Git installed ([Download](https://git-scm.com/))
- A Sarvam AI account (Free - [Sign up](https://www.sarvam.ai/))
- 5 minutes to get API key

---

## **STEP 1: Get Sarvam API Key (5 minutes)**

1. Go to https://www.sarvam.ai/
2. Click "Sign Up" → Create free account
3. Go to Dashboard → "API Keys"
4. Create new API key
5. Copy the key (looks like: `sk_live_xxxxxxxxxxxxx`)
6. **Save it somewhere safe!**

> 💡 Apply for startup programme after signup for ₹1,000 free credits

---

## **STEP 2: Setup Project (5 minutes)**

### **On Windows (Command Prompt):**
```bash
# Clone or download project
cd telecom-ai-bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **On Mac/Linux (Terminal):**
```bash
cd telecom-ai-bot

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

✅ **Check if working:**
```bash
python --version
pip list
```

---

## **STEP 3: Configure API Key (2 minutes)**

Open `.env` file and replace:

```env
SARVAM_API_KEY=your_api_key_here
```

With your actual key:

```env
SARVAM_API_KEY=sk_live_abcd1234efgh5678ijkl
```

Save file.

---

## **STEP 4: Test Connection (3 minutes)**

Run:
```bash
python test_sarvam_connection.py
```

You should see:
```
✓ API Key found: sk_live_abc...
✓ Hindi TTS working!
✓ Tamil TTS working!
✓ Telugu TTS working!
✓ English TTS working!
✓ Translation working!
✓ Sarvam AI is properly configured!
```

If you see errors:
- Double-check API key is correct
- Make sure internet connection is working
- Verify .env file format

---

## **STEP 5: Start Backend Server (5 minutes)**

Open a **NEW terminal window** (keep venv activated):

```bash
# Make sure you're in the right directory
cd telecom-ai-bot

# If needed, activate venv again
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Start the server
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## **STEP 6: Test API Endpoints (5 minutes)**

Open browser: http://localhost:8000/docs

You'll see **Swagger UI** with all API endpoints.

### **Try These:**

1. **Health Check**
   - Click: `GET /health`
   - Click "Try it out" → "Execute"
   - See: `{"status": "healthy"}`

2. **Chat**
   - Click: `POST /chat`
   - Click "Try it out"
   - Paste this in "Request body":
   ```json
   {
     "text": "नमस्कार, मेरी डेटा प्लान क्या है?",
     "language": "hi",
     "user_id": "test_user"
   }
   ```
   - Click "Execute"
   - See bot response in Hindi!

3. **Language Detection**
   - Click: `POST /detect-language`
   - Paste: `"नमस्कार"`
   - Click "Execute"
   - See: `"detected_language": "hi"`

4. **Text-to-Speech**
   - Click: `POST /text-to-speech`
   - Parameters: `text=नमस्कार&language=hi`
   - Click "Execute"
   - Download audio file!

---

## **STEP 7: Open Frontend (5 minutes)**

### **Option A: Simple Python Server**
```bash
# Open NEW terminal in frontend folder
cd frontend
python -m http.server 5000
```

Then open: http://localhost:5000

### **Option B: Using VS Code**
1. Install "Live Server" extension
2. Right-click `index.html`
3. Click "Open with Live Server"

---

## **PROJECT STRUCTURE EXPLAINED**

```
telecom-ai-bot/
├── main.py                    # FastAPI backend
├── test_sarvam_connection.py # API tests
├── requirements.txt           # Dependencies
├── .env                       # Configuration (API keys)
├── .gitignore                # Files to ignore
│
├── frontend/
│   └── index.html            # Phone interface
│
├── backend/
│   └── (Rasa files go here)
│
├── data/
│   └── telecom_bot.db        # Database
│
└── README.md                 # Documentation
```

---

## **API ENDPOINTS QUICK REFERENCE**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Check if API is running |
| POST | `/chat` | Send text message, get response |
| POST | `/detect-language` | Detect language of text |
| POST | `/translate` | Translate between languages |
| POST | `/text-to-speech` | Convert text to audio |
| POST | `/speech-to-text` | Convert audio to text |
| GET | `/user/{user_id}` | Get user profile |

---

## **TESTING CHECKLIST**

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured with API key
- [ ] `test_sarvam_connection.py` passes
- [ ] Backend running on port 8000
- [ ] Frontend accessible
- [ ] Can send/receive chat messages
- [ ] Audio generation working

---

## **COMMON ISSUES & SOLUTIONS**

### **Issue: "ModuleNotFoundError: No module named 'fastapi'"**
**Solution:** 
```bash
# Make sure venv is activated
# Then reinstall
pip install -r requirements.txt
```

### **Issue: "SARVAM_API_KEY not set"**
**Solution:**
- Check .env file exists
- Verify it has `SARVAM_API_KEY=your_key`
- No spaces around `=`
- Restart Python script

### **Issue: Connection refused on port 8000**
**Solution:**
```bash
# Port might be in use, use different port
python main.py --port 8001
```

### **Issue: Frontend can't reach backend**
**Solution:**
```
Check CORS in main.py is enabled (it is by default)
Make sure backend is running
Check frontend is calling http://localhost:8000
```

### **Issue: Audio not generating**
**Solution:**
- Verify Sarvam API key is correct
- Check internet connection
- Verify language code (hi, ta, te, en)
- Check Sarvam dashboard for API usage

---

## **NEXT STEPS AFTER SETUP**

### **Phase 1: Test Core Features ✓ (You are here)**
- Chat in multiple languages
- Audio generation
- Language detection

### **Phase 2: Add Real Rasa (This week)**
- Integrate Rasa NLU
- Create telecom-specific intents
- Add dialogue flows

### **Phase 3: Add Real Voice (Next week)**
- Record audio input
- Process with Sarvam STT
- Full voice conversation

### **Phase 4: Deploy (Next month)**
- Push to Hugging Face Spaces
- Share with team
- Get feedback

---

## **HELPFUL COMMANDS**

```bash
# Check if virtual environment is active
# Should show (venv) at start of terminal line

# Activate venv (always do this first!)
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Deactivate venv (when done)
deactivate

# Install new package
pip install package_name

# List installed packages
pip list

# See full project structure
tree  # or 'ls -R' on Mac/Linux

# Stop running server
# Press Ctrl + C in terminal

# Run tests
python -m pytest

# View API docs
# Go to http://localhost:8000/docs
```

---

## **KEYBOARD SHORTCUTS**

- `Ctrl + C` - Stop running server
- `Ctrl + L` - Clear terminal screen
- `Up Arrow` - Previous command
- `Ctrl + Shift + T` - Open new terminal

---

## **GETTING HELP**

1. **API Documentation**: http://localhost:8000/docs
2. **Sarvam Docs**: https://docs.sarvam.ai/
3. **FastAPI Docs**: https://fastapi.tiangolo.com/
4. **Common Issues**: Check the "Common Issues" section above

---

## **SUCCESS! 🎉**

You now have:
- ✅ Working multilingual chat bot
- ✅ Text-to-speech in Indian languages
- ✅ Language detection
- ✅ Translation between languages
- ✅ Web interface
- ✅ API documentation

**Next: Read the full TELECOM_AI_PROJECT_GUIDE.md for advanced features!**

---

**Built with ❤️ for Indian telecom customers**
