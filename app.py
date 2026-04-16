from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# API KEY dari Render
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# SYSTEM PROMPT (versi stabil & pintar)
system_prompt = """
Kamu adalah AI pribadi milik user (Tuan DF).

ATURAN WAJIB:
- Selalu jawab pertanyaan user
- Jawaban harus relevan dengan pertanyaan
- Jawaban singkat (maksimal 1-2 kalimat kecuali diminta panjang)
- Jangan keluar topik
- Jangan bertele-tele
- Gunakan bahasa santai tapi tetap jelas
- Jangan sok pintar atau ngawur

PERILAKU:
- Anggap user adalah pemilik kamu
- Fokus membantu user secepat dan sejelas mungkin
- Jika user hanya bilang "halo", jawab "Halo Tuan"
- Jika tidak yakin, tetap jawab dengan versi paling masuk akal

GAYA BICARA:
- Santai
- Tegas
- Seperti asisten pintar (Jarvis versi santai)
"""

@app.route("/")
def home():
    return "Backend Groq jalan 🚀"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("message")
        history = data.get("history", [])

        if not user_input:
            return jsonify({"error": "no input"})

        # Susun messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]

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
            }
        )

        result = response.json()

        if "choices" not in result:
            return jsonify({"error": result})

        reply = result["choices"][0]["message"]["content"]

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run()
