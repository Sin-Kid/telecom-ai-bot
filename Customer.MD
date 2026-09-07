# Customer Database — TeleBot AI Demo

This document lists all demo customer profiles configured for **TeleBot AI**. The bot dynamically loads the correct profile based on the caller's phone number.

---

## 📋 All Customer Profiles

| # | Name | Phone | Operator | Plan | Data/Day | Remaining | Validity | Bill Due |
|---|------|-------|----------|------|----------|-----------|----------|---------|
| 1 | **Pavan** | `6360341569` | Airtel | ₹449 | 2 GB | **1.5 GB** | 28 days | ₹450 |
| 2 | **Aarav Sharma** | `9876543210` | Jio | ₹299 | 1.5 GB | **0.8 GB** | 28 days | ₹0 |
| 3 | **Priya Nair** | `8765432109` | Airtel | ₹719 | 2 GB | **1.2 GB** | 84 days | ₹0 |
| 4 | **Rohit Verma** | `7654321098` | Vi | ₹479 | 1.5 GB | **1.5 GB** | 56 days | ₹120.50 |
| 5 | **Kavitha Reddy** | `9543210987` | Airtel | ₹449 | 2 GB | **0.3 GB** | 28 days | ₹0 |
| 6 | **Arjun Mehta** | `8432109876` | Jio | ₹999 | 2 GB | **2.0 GB** | 84 days | ₹0 |
| 7 | **Meena Iyer** | `7321098765` | BSNL | ₹197 | 2 GB | **1.8 GB** | 28 days | ₹75 |
| 8 | **Siddharth Kulkarni** | `9210987654` | Vi | ₹359 | 1 GB | **0.5 GB** | 28 days | ₹230 |
| 9 | **Divya Krishnamurthy** | `8109876543` | Airtel | ₹599 | 2 GB | **1.0 GB** | 56 days | ₹0 |
| 10 | **Rahul Bose** | `7098765432` | Jio | ₹399 | 2 GB | **0.1 GB** | 28 days | ₹0 |
| 11 | **Anjali Singh** | `9988776655` | Airtel | ₹249 | 1 GB | **0.7 GB** | 28 days | ₹50 |

---

## 🔧 How It Works

The AI bot dynamically personalizes responses based on the caller's phone number:

1. **Frontend** sends `phone` field in the `/chat` API request.
2. **Backend** (`main.py`) looks up the matching profile in `customers.json`.
3. **System prompt** is rebuilt with that customer's real data.
4. **LLM** (Llama 3.2) responds with accurate, personalized info.

### Example

> **Kavitha** asks: *"What's my data balance?"*
> → Bot: *"Hi Kavitha! You have only **0.3 GB** left today out of your 2 GB daily limit on your Airtel ₹449 plan."*

> **Arjun** asks the same question:
> → Bot: *"Hi Arjun! Great news — you have the full **2.0 GB** remaining today on your Jio ₹999 plan!"*

---

## 📂 Files

| File | Purpose |
|------|---------|
| [`customers.json`](file:///Users/pavang/Documents/DSA-EL/telecom-ai-bot/customers.json) | Customer database (phone → profile mapping) |
| [`system_prompt.txt`](file:///Users/pavang/Documents/DSA-EL/telecom-ai-bot/system_prompt.txt) | Base system prompt (customer block overridden dynamically) |
| [`main.py`](file:///Users/pavang/Documents/DSA-EL/telecom-ai-bot/main.py) | `get_customer()` + `build_system_prompt()` |

---

## 🌐 Admin API

View all loaded customers at runtime:
```
GET http://localhost:8000/customers
```
