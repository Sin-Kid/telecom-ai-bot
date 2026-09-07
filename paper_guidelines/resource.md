# Project Resources & Raw Data for Paper

This document contains the raw data, system architecture details, and customer report examples needed to draft the technical sections of your IEEE paper. You can copy-paste these details directly into your AI editing tool (like Prism) as supporting context.

---

## 1. System Architecture & Tech Stack

**Core Architecture (Fully Local & Privacy-Focused):**
- **Brain / LLM Engine:** Ollama running Llama 3.2 locally.
- **Backend API:** FastAPI (Python 3.10/3.13) running on Uvicorn.
- **Text-To-Speech (TTS) Engine:** AI4Bharat / Coqui TTS (FastPitch + HiFi-GAN) for natural voice output.
- **Hardware Acceleration:** Mac Metal Performance Shaders (MPS) for fast voice synthesis.
- **Supported Languages:** Kannada, Hindi, Tamil, Telugu, English, Bengali, Marathi.

**Dynamic Personalization Workflow (Use-case Diagram Flow):**
1. **Input:** The Frontend sends the user's `phone` number and query via the `/chat` API request.
2. **Lookup:** The Backend (`main.py`) looks up the matching customer profile in the `customers.json` database.
3. **Prompt Injection:** The base `system_prompt.txt` is dynamically rebuilt using the user's real-time data (e.g., remaining data balance, bill due).
4. **Inference:** Llama 3.2 processes the prompt and the user's query to generate a highly personalized, context-aware response.
5. **Output:** The TTS engine synthesizes the response into the user's preferred regional language and sends the audio/text back to the frontend.

---

## 2. Customer Database (`customers.json` / `Customer.MD`)

The system maps callers to their respective telecom plans to provide accurate support. Here is a snapshot of the dataset structure:

| # | Name | Phone | Operator | Plan | Data/Day | Remaining | Validity | Bill Due |
|---|------|-------|----------|------|----------|-----------|----------|---------|
| 1 | Pavan | `6360341569` | Airtel | ₹449 | 2 GB | 1.5 GB | 28 days | ₹450 |
| 2 | Aarav Sharma | `9876543210` | Jio | ₹299 | 1.5 GB | 0.8 GB | 28 days | ₹0 |
| 3 | Priya Nair | `8765432109` | Airtel | ₹719 | 2 GB | 1.2 GB | 84 days | ₹0 |
| 4 | Rohit Verma | `7654321098` | Vi | ₹479 | 1.5 GB | 1.5 GB | 56 days | ₹120.50 |

**Example Interaction:**
- **User (Kavitha):** "What's my data balance?"
- **Bot Response:** "Hi Kavitha! You have only 0.3 GB left today out of your 2 GB daily limit on your Airtel ₹449 plan."

---

## 3. Customer Reports (`customer_reports.csv`)

This dataset tracks the interactions, latency, and language usage for performance metrics. 

**Dataset Schema:**
`Timestamp, User ID, Language, User Query, Bot Response, Duration (s)`

**Sample Data:**
1. **EN Query:** "Hello! Welcome to our telecom support..."
   - *Query:* "hi"
   - *Latency:* 11.37 seconds
2. **HI Query:** "Check my data balance"
   - *Response:* "आपके प्लान की विशेषता और डेटा बैलेंस को देखने के लिए, कृपया अपना मोबाइल नंबर या ऑटोप्लेन नंबर दें।"
   - *Latency:* 7.11 seconds
3. **HI Query:** "Show recharge plans"
   - *Response:* "संचार योजनाओं की सूची। 1. डेथ स्टिक रिचार्ज प्लान - ₹499/महीना..."
   - *Latency:* 12.52 seconds

---

## 4. Performance Metrics (For Results Section)

When writing your Results/Methodology section, you can define these parameters based on the CSV data:
- **Average API Latency:** ~6 to 12 seconds (depending on translation/TTS processing and LLM inference time).
- **Multilingual Accuracy:** Handled via `deep-translator` and native Indic-TTS models.
- **Resource Utilization:** Optimized using Mac MPS for local offline inferencing without relying on cloud APIs, ensuring 100% data privacy for customer records.

---
*Tip: Feed this document into Prism alongside your IEEE Master Prompt to ensure the AI uses real data and architectures from your project!*
