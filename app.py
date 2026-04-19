from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import random

app = Flask(__name__)
CORS(app)

# API KEY dari Render
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# MEMORY CHAT (sementara, hilang kalau server restart)
chat_memory = {}

# SYSTEM PROMPT (JARVIS FULL)
system_prompt = """
Kamu adalah Jarvis, asisten pribadi milik Tuan DF.

IDENTITAS:
- Nama: Jarvis
- Peran: Asisten pribadi digital
- Tugas: Membantu user menjawab, memberi solusi, dan menemani percakapan

ATURAN:
- Jawab singkat, jelas, tidak bertele-tele
- Maksimal 2-3 kalimat (kecuali diminta panjang)
- Gunakan bahasa santai tapi tetap sopan
- Jangan keluar topik

GAYA:
- Seperti asisten pintar (Jarvis Iron Man versi santai)
- Natural, tidak kaku
- Sedikit berkarakter

PERILAKU:
- Anggap user adalah Tuan kamu
- Selalu siap membantu
- Kalau tidak yakin, jawab versi paling masuk akal

KHUSUS:
- Jika user bertanya "kamu siapa", jawab bahwa kamu adalah Jarvis, asisten pribadi Tuan DF
- Jika user menyapa ("halo", "hai"), jawab:
  "Halo Tuan, Jarvis siap membantu."
- Jika percakapan santai, boleh balas santai juga
"""

@app.route("/")
def home():
    return "Backend Jarvis aktif 🚀"

@app.route("/chat", methods=["GET", "POST"])
def chat():
    try:
        # Handle GET
        if request.method == "GET":
            return "CHAT READY ✅"

        data = request.get_json(force=True)
        print("DATA MASUK:", data)

        user_input = data.get("message", "")
        sender = data.get("sender", "user")
        is_group = data.get("isGroup", False)

        # ❌ Jangan balas grup
        if is_group:
            return jsonify({"replies": []})

        # Jika kosong
        if not user_input:
            return jsonify({
                "replies": [{"message": "..."}]
            })

        text = user_input.lower()

        # =========================
        # 🔥 MODE "TUAN SEDANG TIDAK ADA"
        # =========================
        keywords = [
            "mana", "dimana", "ke mana",
            "kemana", "lagi dimana",
            "kok ga bales", "tidak balas",
            "kenapa ga jawab", "kenapa tidak jawab"
        ]

        if any(k in text for k in keywords):
            responses = [
                "Saat ini Tuan DF sedang tidak berada di tempat. Untuk sementara, saya Jarvis yang akan membantu Anda.",
                "Tuan DF sedang tidak menggunakan handphonenya saat ini. Saya Jarvis siap membantu jika diperlukan.",
                "Mohon maaf, Tuan DF sedang tidak tersedia. Saya Jarvis akan mewakili untuk merespon pesan Anda.",
                "Saat ini Tuan DF sedang tidak aktif di perangkatnya. Saya Jarvis akan membantu sementara."
            ]

            reply = random.choice(responses)

            return jsonify({
                "replies": [
                    {"message": reply}
                ]
            })

        # =========================
        # 💾 MEMORY PER USER
        # =========================
        if sender not in chat_memory:
            chat_memory[sender] = []

        history = chat_memory[sender]

        messages = [{"role": "system", "content": system_prompt}]
        messages += history[-6:]  # ambil 6 pesan terakhir

        messages.append({
            "role": "user",
            "content": user_input
        })

        # =========================
        # 🤖 REQUEST KE GROQ
        # =========================
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
                "max_tokens": 150
            },
            timeout=10
        )

        result = response.json()
        print("RESPONSE GROQ:", result)

        if "choices" not in result:
            return jsonify({
                "replies": [
                    {"message": "Jarvis sedang mengalami gangguan kecil."}
                ]
            })

        reply_ai = result["choices"][0]["message"]["content"]

        # Simpan ke memory
        chat_memory[sender].append({
            "role": "user",
            "content": user_input
        })
        chat_memory[sender].append({
            "role": "assistant",
            "content": reply_ai
        })

        # =========================
        # 🤖 INTRO JARVIS (HANYA AWAL)
        # =========================
        if len(chat_memory[sender]) <= 2:
            final_reply = f"Anda terhubung dengan Jarvis, asisten pribadi Tuan DF.\n\n{reply_ai}"
        else:
            final_reply = reply_ai

        # =========================
        # 📤 RETURN KE AUTORESPONDER
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
                {"message": "Server sedang sibuk, coba lagi nanti."}
            ]
        })

if __name__ == "__main__":
    app.run()
