from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

# ✅ INI HARUS DI ATAS
app = Flask(__name__)
CORS(app)

# API KEY
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# SYSTEM PROMPT
system_prompt = """
Kamu adalah AI pribadi milik user (Tuan DF).
...
"""

# ✅ ROUTE SETELAH app DIBUAT
@app.route("/")
def home():
    return "Backend Groq jalan 🚀"

@app.route("/chat", methods=["GET", "POST"])
def chat():
    try:
        if request.method == "GET":
            return "CHAT READY ✅"

        data = request.get_json(force=True)

        user_input = data.get("message", "")
        history = data.get("history", [])

        if not user_input:
            return jsonify({"reply": "..."})

        messages = [{"role": "system", "content": system_prompt}]

        for msg in history:
            messages.append(msg)

        messages.append({
            "role": "user",
            "content": user_input
        })

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 150
            },
            timeout=10
        )

        result = response.json()

        if "choices" not in result:
            return jsonify({"reply": "Lagi error bentar"})

        reply = result["choices"][0]["message"]["content"]

        return jsonify({"reply": reply})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"reply": "Server lagi sibuk"})
