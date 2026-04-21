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
# MEMORY + STATE
# =========================
chat_memory = {}
chat_state = {}

# =========================
# SYSTEM PROMPT
# =========================
system_prompt = """
Kamu adalah Jarvis, asisten pribadi milik Tuan DF.

ATURAN:
- Jawab sangat singkat, maksimal 2 kalimat.
- Gaya elegan, tenang, sopan.
- Selalu panggil user dengan "Tuan".

ALUR WAJIB:
1. Pesan pertama: "Tuan, ada pesan dari [nama]. Mau saya bacakan?"
2. Jika Tuan jawab ya/bacakan → bacakan isi pesannya.
3. Setelah dibacakan → tanyakan "Mau membalas pesan ini?"
4. Jika Tuan jawab ya/balas → jawab "Silakan Tuan, katakan apa yang ingin dibalas."
5. Jika Tuan diam saja → jawab "Anda terhubung dengan Jarvis, asisten pribadi Tuan DF."
"""

# =========================
# TEXT TO SPEECH - SUDAH DIFIX (MODEL DI HEADER)
# =========================
def text_to_speech(text):
    try:
        if not text or len(text.strip()) < 3:
            print("TTS: Text terlalu pendek")
            return ""

        url = "https://api.fish.audio/v1/tts"

        headers = {
            "Authorization": f"Bearer {FISH_API_KEY}",
            "Content-Type": "application/json",
            "model": "s1"                    # ← INI YANG PENTING (di HEADER)
        }

        data = {
            "text": text.strip()[:500]
        }

        r = requests.post(url, json=data, headers=headers, timeout=15)

        if r.status_code != 200:
            print("❌ FISH TTS ERROR:", r.status_code, r.text)
            return ""

        # Simpan file
        os.makedirs("static", exist_ok=True)
        filename = f"jarvis_{random.randint(10000,99999)}.mp3"
        file_path = f"static/{filename}"

        with open(file_path, "wb") as f:
            f.write(r.content)

        # Hardcoded URL untuk Render
        base_url = "https://ai-backend-0d98.onrender.com"
        audio_url = f"{base_url}/static/{filename}"

        print(f"✅ TTS BERHASIL → {audio_url}")
        return audio_url

    except Exception as e:
        print("❌ TTS EXCEPTION:", str(e))
        return ""


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
        query = data.get("query", {})

        user_input = query.get("message", "").strip()
        sender = query.get("sender", "unknown")
        sender_name = query.get("senderName", sender)
        is_group = query.get("isGroup", False)

        if is_group:
            return jsonify({"message": "", "audio": "", "state": "idle"})

        if sender not in chat_memory:
            chat_memory[sender] = []
        if sender not in chat_state:
            chat_state[sender] = "idle"

        # Pesan pertama dari WhatsApp
        if not user_input and chat_state[sender] == "idle":
            final_reply = f"Tuan, ada pesan dari {sender_name}.\nMau saya bacakan?"

            audio_url = text_to_speech(final_reply)
            chat_memory[sender].append({"role": "assistant", "content": final_reply})
            chat_state[sender] = "waiting_read"

            return jsonify({
                "message": final_reply,
                "audio": audio_url,
                "state": chat_state[sender]
            })

        # Proses AI
        messages = [{"role": "system", "content": system_prompt}]
        messages += chat_memory[sender][-8:]
        messages.append({"role": "user", "content": user_input})

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": messages,
                    "temperature": 0.5,
                    "max_tokens": 130
                },
                timeout=10
            )
            result = response.json()
            reply_ai = result["choices"][0]["message"]["content"] if "choices" in result else "Maaf Tuan."
        except Exception as e:
            print("GROQ ERROR:", str(e))
            reply_ai = "Saya sedang memproses, Tuan."

        chat_memory[sender].append({"role": "user", "content": user_input})
        chat_memory[sender].append({"role": "assistant", "content": reply_ai})

        # Update state
        text_lower = user_input.lower()
        if any(word in text_lower for word in ["ya", "bacakan", "baca"]):
            chat_state[sender] = "waiting_reply"
        elif any(word in text_lower for word in ["balas", "ya"]) and chat_state[sender] == "waiting_reply":
            chat_state[sender] = "reply_mode"

        audio_url = text_to_speech(reply_ai)

        return jsonify({
            "message": reply_ai,
            "audio": audio_url,
            "state": chat_state[sender]
        })

    except Exception as e:
        print("ERROR UTAMA:", str(e))
        return jsonify({"message": "Gangguan sementara.", "audio": "", "state": "idle"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
