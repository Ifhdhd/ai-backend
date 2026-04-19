from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import random

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

chat_memory = {}

system_prompt = """
Kamu adalah Jarvis, asisten pribadi milik Tuan DF.

- Jawab singkat, jelas, santai
- Maksimal 2-3 kalimat
- Kalau ditanya siapa kamu, jawab kamu Jarvis
- Kalau disapa: "Halo Tuan, Jarvis siap membantu."
"""

@app.route("/")
def home():
    return "Jarvis backend aktif 🚀"

@app.route("/chat", methods=["GET", "POST"])
def chat():
    try:
        if request.method == "GET":
            return "CHAT READY ✅"

        data = request.get_json(force=True)
        print("DATA MASUK:", data)

        # 🔥 FIX UTAMA (AMBIL DARI QUERY)
        query = data.get("query", {})

        user_input = query.get("message", "")
        sender = query.get("sender", "user")
        is_group = query.get("isGroup", False)

        if is_group:
            return jsonify({"replies": []})

        if not user_input:
            return jsonify({
                "replies": [{"message": "Jarvis siap membantu."}]
            })

        text = user_input.lower()

        # =========================
        # MODE TUAN TIDAK ADA
        # =========================
        keywords = [
            "mana", "dimana", "kemana",
            "kok ga bales", "kenapa ga jawab",
            "lagi dimana"
        ]

        if any(k in text for k in keywords):
            responses = [
                "Saat ini Tuan DF sedang tidak berada di tempat. Saya Jarvis akan membantu Anda sementara.",
                "Tuan DF sedang tidak menggunakan handphonenya saat ini. Saya Jarvis siap membantu.",
                "Mohon maaf, Tuan DF sedang tidak tersedia. Saya Jarvis yang akan merespon pesan Anda."
            ]

            return jsonify({
                "replies": [{"message": random.choice(responses)}]
            })

        # =========================
        # MEMORY
        # =========================
        if sender not in chat_memory:
            chat_memory[sender] = []

        history = chat_memory[sender]

        messages = [{"role": "system", "content": system_prompt}]
        messages += history[-4:]
        messages.append({"role": "user", "content": user_input})

        # =========================
        # AI REQUEST (ANTI TIMEOUT)
        # =========================
        reply_ai = "Jarvis sedang memproses..."

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": messages,
                    "temperature": 0.4,
                    "max_tokens": 100
                },
                timeout=6
            )

            result = response.json()

            if "choices" in result:
                reply_ai = result["choices"][0]["message"]["content"]

        except Exception as e:
            print("AI ERROR:", str(e))

        # simpan memory
        chat_memory[sender].append({"role": "user", "content": user_input})
        chat_memory[sender].append({"role": "assistant", "content": reply_ai})

        # =========================
        # INTRO (HANYA AWAL)
        # =========================
        if len(chat_memory[sender]) <= 2:
            final_reply = f"Anda terhubung dengan Jarvis, asisten pribadi Tuan DF.\n\n{reply_ai}"
        else:
            final_reply = reply_ai

        # =========================
        # RETURN KE AUTORESPONDER
        # =========================
        return jsonify({
            "replies": [
                {"message": final_reply}
            ]
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "replies": [
                {"message": "Jarvis sedang mengalami gangguan."}
            ]
        })

if __name__ == "__main__":
    app.run()
