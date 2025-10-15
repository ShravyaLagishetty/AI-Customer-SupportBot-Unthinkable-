"""
llm_adapter.py — Auto-Detecting OpenRouter Integration
Author: ChatGPT-5 (2025)
"""

import os
import requests

# Environment setup
API_KEY = os.getenv("AI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openrouter")
API_URL = "https://openrouter.ai/api/v1/chat/completions"


def get_available_models():
    """Fetch the list of models your OpenRouter key can access."""
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        r = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        models = [m["id"] for m in data.get("data", [])]
        return models
    except Exception as e:
        print(f"⚠️ Could not fetch model list: {e}")
        return []


def pick_best_model():
    """Select the best available model automatically."""
    preferred_order = [
        "mistralai/mixtral-8x22b",
        "meta-llama/llama-3.1-70b-instruct",
        "anthropic/claude-3-haiku",
        "openai/gpt-4o-mini",
        "google/gemma-2-9b-it",
    ]

    models = get_available_models()
    if not models:
        print("⚠️ No models found from OpenRouter; using safe default.")
        return "openai/gpt-4o-mini"

    for model in preferred_order:
        if model in models:
            print(f"✅ Using available model: {model}")
            return model

    print(f"⚠️ Preferred models not found. Using fallback: {models[0]}")
    return models[0]


# Auto-select if MODEL_NAME not set
if not MODEL_NAME:
    MODEL_NAME = pick_best_model()


def call_openrouter_api(prompt, history=None):
    """Send chat request to OpenRouter."""
    if not API_KEY:
        raise ValueError("⚠️ OpenRouter API key not set. Define AI_API_KEY environment variable.")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "AI Customer Support Bot",
        "Content-Type": "application/json",
    }

    messages = []
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 512,
    }

    print(f"🔍 Sending request to OpenRouter model: {MODEL_NAME}")
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)

    if response.status_code != 200:
        raise RuntimeError(f"OpenRouter API error: {response.status_code} {response.text}")

    data = response.json()
    return data["choices"][0]["message"]["content"]


def generate_reply(user_text, history=None, db=None):
    """Main chatbot logic used by FastAPI backend."""
    system_prompt = (
        "You are HelpBot, a friendly and professional AI customer support assistant. "
        "Answer user queries clearly using the company's FAQ knowledge. "
        "If unsure, say 'I'm not sure — I can escalate this to a human agent.' "
        "Always include one brief suggested next step."
    )

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    try:
        reply = call_openrouter_api(user_text, history=messages)
        confidence = 0.9
        suggested_action = None

        if any(word in user_text.lower() for word in ["refund", "cancel", "dispute", "lost", "charge", "damaged", "broken", "issue", "problem", "late"]):
           confidence = 0.5
           suggested_action = {"type": "open_ticket", "priority": "high"}

        if any(k in reply.lower() for k in ["ticket", "escalate", "agent", "support team"]):
           suggested_action = {"type": "open_ticket", "priority": "medium"}

        return reply.strip(), suggested_action, confidence

    except Exception as e:
        return f"⚠️ OpenRouter API error: {e}", None, 0.3
