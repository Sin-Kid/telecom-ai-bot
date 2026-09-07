# Telecom AI Bot (Fully Local)

A privacy-focused, 100% offline multilingual telecom assistant. This bot runs locally on your Mac using **Ollama** for intelligence and **Indic-TTS** for natural voice output in Indian languages.

## 🚀 Tech Stack
- **Brain**: Ollama (running Llama 3.2)
- **Backend**: FastAPI (Python 3.10/3.13)
- **TTS Engine**: AI4Bharat / Coqui TTS (FastPitch + HiFi-GAN)
- **Voice Acceleration**: Mac Metal Performance Shaders (MPS)
- **Languages**: Kannada, Hindi, Tamil, Telugu, English, Bengali, Marathi

---

## 🛠️ Quick Setup

### 1. Start the Brain (Ollama)
Ensure Ollama is running with Llama 3.2:
```bash
ollama run llama3.2
```

### 2. Activate the Environment
Use the dedicated Conda environment for TTS:
```bash
conda activate tts-env
```

### 3. Install Dependencies
If you're on a new setup, install the core libraries:
```bash
pip install fastapi uvicorn requests python-dotenv soundfile coqpit trainer gruut mecab-python3 unidic-lite jieba deep-translator
```

---

## 🎙️ Running Synthesis (CLI)

To generate speech from the command line:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/TTS
python3 TTS/TTS/bin/synthesize.py \
  --text "ನಮಸ್ಕಾರ, ಇದು ಕನ್ನಡ ಪರೀಕ್ಷೆ" \
  --model_path models/indic-tts/kannada/fastpitch/best_model.pth \
  --config_path models/indic-tts/kannada/fastpitch/config.json \
  --vocoder_path models/indic-tts/kannada/hifigan/best_model.pth \
  --vocoder_config_path models/indic-tts/kannada/hifigan/config.json \
  --speaker_id female \
  --out_path output.wav
```

---

## 🤖 Running the Full Bot (API)

To start the FastAPI backend and Ollama automatically:
```bash
./start.sh
```

*(Alternatively, to start manually without stopping other services)*:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/TTS
python3 telecom-ai-bot/main.py
```

The server will be available at `http://0.0.0.0:8000`.

---

## 📁 Project Structure
- `telecom-ai-bot/`: Backend API and logic.
- `models/`: Pre-trained FastPitch and HiFi-GAN weights.
- `TTS/`: Core Coqui TTS library.
- `frontend/`: Web interface for the bot.
