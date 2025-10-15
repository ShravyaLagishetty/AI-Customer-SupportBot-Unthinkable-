# AI Customer Support Bot

An intelligent, full-stack **AI-powered customer support chatbot** built using **FastAPI**, **React (Vite)**, **Tailwind CSS**, and **OpenRouter AI Models**.  
The system answers FAQs, maintains chat context, and escalates unresolved queries to human support — with a clean, black-glass modern UI.

---

## Key Features

**AI-Powered Conversations**  
• Uses OpenRouter LLM (Mixtral / Llama 3 / GPT-4o-mini) for realistic answers  
• Automatically picks the best available model  

 **Session & Memory**  
• Redis for short-term memory (last N messages)  
• PostgreSQL for full conversation history  

**Escalation System**  
• Automatic escalation when model confidence < threshold  
• Manual “Escalate” button in UI  

**Frontend (Chat UI)**  
• Built with React + Vite + Tailwind CSS + Framer Motion  
• Black background + glass chat window + gradient header  
• Avatars, timestamps, smooth animations, fully responsive  

**Backend (FastAPI)**  
• REST API for sessions, messages, escalation, feedback  
• Celery + Redis for async background tasks  
• Integrated OpenRouter API for LLM replies  

---

## 🧠 System Architecture

Frontend (React + Tailwind + Vite)
│
▼
FastAPI Backend (Python)
│
▼
OpenRouter API (LLM)
│
├── Redis (short-term memory)
└── PostgreSQL (session logs)

yaml
Copy code

---

## Tech Stack

| Layer | Technology |
|--------|-------------|
| Frontend | React (Vite), Tailwind CSS, Framer Motion, Axios |
| Backend | FastAPI, Python 3.11 |
| AI / LLM | OpenRouter API (Mixtral / Llama / GPT models) |
| Cache | Redis |
| Database | PostgreSQL |
| Queue / Tasks | Celery |
| Vector DB | FAISS (optional) |

---

## Project Structure

ai-customer-support-bot/
├── backend/
│ ├── app/
│ │ ├── main.py
│ │ ├── llm_adapter.py
│ │ └── worker.py
│ ├── requirements.txt
│ └── .env
│
├── frontend/
│ ├── chat-ui/
│ │ ├── src/App.jsx
│ │ ├── package.json
│ │ ├── tailwind.config.js
│ │ └── vite.config.js
│ └── react-admin/ (optional dashboard)
│
├── .gitignore
└── README.md

yaml
Copy code

---

## Setup Instructions

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Create a .env file inside backend/:

ini
Copy code
AI_API_KEY=sk-or-v1-your-openrouter-api-key
MODEL_PROVIDER=openrouter
Run backend:

bash
Copy code
uvicorn app.main:app --reload --port 8000
👉 Runs on http://localhost:8000

Frontend (Chat UI)
bash
Copy code
cd ../frontend/chat-ui
npm install
npm run dev
👉 Open http://localhost:5173 in browser.

⚡ Redis & Celery (optional for memory + background tasks)
Start Redis (Windows example):

bash
Copy code
cd "C:\Users\<YourUser>\Downloads\Redis-x64-3.2.100"
.\redis-server.exe
Start Celery worker:

bash
Copy code
cd backend
.venv\Scripts\activate
python -m celery -A worker.cel worker --pool=solo --loglevel=info
  How It Works
User clicks New Chat → backend creates session.

Message sent → FastAPI builds prompt + context → calls OpenRouter LLM.

AI returns JSON reply (text + suggested action + confidence).

Response displayed instantly with animation.

Escalation auto-triggers if low confidence or user clicks Escalate.

 API Endpoints
Method	Endpoint	Description
POST	/api/v1/sessions	Create new chat session
POST	/api/v1/sessions/{id}/message	Send message + get AI reply
POST	/api/v1/sessions/{id}/escalate	Escalate current session
POST	/api/v1/feedback	Submit feedback
GET	/api/v1/metrics	Retrieve admin metrics

Swagger Docs → http://localhost:8000/docs


 Security
Environment variables stored in .env (not pushed to Git).

API keys and database secrets excluded via .gitignore.

HTTPS ready for deployment.

** Git Commands Quick Reference
git init
git remote add origin https://github.com/<username>/ai-customer-support-bot.git
git add .
git commit -m "Initial commit - AI Customer Support Bot"
git branch -M main
git push -u origin main

Demo Video link:
https://drive.google.com/file/d/13CtkXjnQgKmp0SSI_KL-OpnAQucFk6ur/view?usp=sharing


