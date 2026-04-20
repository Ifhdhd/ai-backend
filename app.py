from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import random

app = Flask(__name__)
CORS(app)

# =========================
# API KEYS
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FISH_API_KEY = os.getenv("FISH_API_KEY")

# =========================
# MEMORY
# =========================
chat_memory = {}

# =========================
# SYSTEM PROMPT
# =========================
system_prompt = """
Kamu adalah Jarvis, asisten pribadi milik Tuan DF.

ATURAN:
- Jawab singkat, jelas, santai (maks 2 kalimat)
- Gunakan gaya elegan dan tenang
- Panggil user dengan "Tuan"
- Jika ditanya siapa kamu, jawab kamu Jarvis
"""

# =========================
# TEXT TO SPEECH (FISH)
# =========================
def text_to_speech(text):
    try:
        url = "https://api.fish.audio/v1/tts"

        headers = {
            "Authorization": f"Bearer {FISH_API_KEY}",
            "Content-Type": "application/json",
            "model": "s1"
        }

        data = {
            "text": text
        }

        r = requests.post(url, json=data, headers=headers, timeout=10)

        if r.status_code != 200:
            print("FISH ERROR:", r.text)
            return None

        os.makedirs("static", exist_ok=True)

        filename = f"jarvis_{random.randint(1000,9999)}.mp3"
        file_path = f"static/{filename}"

        with open(file_path, "wb") as f:
            f.write(r.content)

        # 🔥 AUTO DOMAIN (PENTING)
        return request.host_url + "static/" + filename

    except Exception as e:
        print("TTS ERROR:", str(e))
        return None


# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return "Jarvis backend aktif 🚀"


@app.route("/static/<path:filename>")
def serve_audio(filename):
    return send_from_directory("static", filename)


@app.route("/chat", methods=["GET", "POST"])
def chat():
    try:
        if request.method == "GET":
            return "CHAT READY ✅"

        data = request.get_json(force=True)
        print("DATA MASUK:", data)

        query = data.get("query", {})

        user_input = query.get("message", "")
        sender = query.get("sender", "user")
        is_group = query.get("isGroup", False)

        if is_group:
            return jsonify({"replies": []})

        if not user_input:
            final_reply = "Jarvis siap membantu."
            audio_url = text_to_speech(final_reply)

            return jsonify({
                "replies": [{"message": final_reply}],
                "audio": audio_url if audio_url else ""
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
                "Saat ini Tuan DF sedang tidak berada di tempat. Saya Jarvis akan membantu Anda.",
                "Tuan DF sedang tidak menggunakan handphonenya. Saya Jarvis siap membantu.",
                "Mohon maaf, Tuan DF sedang tidak tersedia. Saya akan menggantikan sementara."
            ]

            final_reply = random.choice(responses)
            audio_url = text_to_speech(final_reply)

            return jsonify({
                "replies": [{"message": final_reply}],
                "audio": audio_url if audio_url else ""
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
        # GROQ AI
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

        # =========================
        # SIMPAN MEMORY
        # =========================
        chat_memory[sender].append({"role": "user", "content": user_input})
        chat_memory[sender].append({"role": "assistant", "content": reply_ai})

        # =========================
        # INTRO AWAL
        # =========================
        if len(chat_memory[sender]) <= 2:
            final_reply = f"Anda terhubung dengan Jarvis, asisten pribadi Tuan DF.\n\n{reply_ai}"
        else:
            final_reply = reply_ai

        # =========================
        # BUAT AUDIO
        # =========================
        audio_url = text_to_speech(final_reply)

        # =========================
        # RETURN FINAL
        # =========================
        return jsonify({
            "replies": [{"message": final_reply}],
            "audio": audio_url if audio_url else ""
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "replies": [{"message": "Jarvis sedang mengalami gangguan."}],
            "audio": ""
        })


if __name__ == "__main__":
    app.run()
