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
chat_state = {}  # Tambahan state per pengirim

# =========================
# SYSTEM PROMPT (DIOPTIMALKAN)
# =========================
system_prompt = """
Kamu adalah Jarvis, asisten pribadi milik Tuan DF.

ATURAN:
- Jawab sangat singkat, maksimal 2 kalimat.
- Gaya elegan, tenang, sopan.
- Selalu panggil user dengan "Tuan".
- Jika ditanya siapa kamu, jawab: "Saya Jarvis, asisten pribadi Tuan DF."

ALUR WHATSAPP WAJIB:
1. Pesan pertama masuk: Beritahu ada pesan dari siapa, lalu tanyakan "Mau saya bacakan?"
2. Jika Tuan jawab ya/bacakan → bacakan isi pesannya dengan jelas.
3. Setelah dibacakan → tanyakan "Mau membalas pesan ini?"
4. Jika Tuan jawab ya/balas → jawab: "Silakan Tuan, katakan apa yang ingin dibalas."
5. Jika Tuan diam saja → jawab: "Anda terhubung dengan Jarvis, asisten pribadi Tuan DF."
"""

# =========================
# TEXT TO SPEECH (FISH s1)
# =========================
def text_to_speech(text):
    try:
        url = "https://api.fish.audio/v1/tts"

        headers = {
            "Authorization": f"Bearer {FISH_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "text": text,
            "model": "s1"          # sesuai keinginanmu
        }

        r = requests.post(url, json=data, headers=headers, timeout=10)

        if r.status_code != 200:
            print("FISH ERROR:", r.text)
            return ""

        os.makedirs("static", exist_ok=True)
        filename = f"jarvis_{random.randint(1000,9999)}.mp3"
        file_path = f"static/{filename}"

        with open(file_path, "wb") as f:
            f.write(r.content)

        return request.host_url + "static/" + filename

    except Exception as e:
        print("TTS ERROR:", str(e))
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
            return jsonify({"message": "", "audio": ""})

        # Inisialisasi memory & state
        if sender not in chat_memory:
            chat_memory[sender] = []
        if sender not in chat_state:
            chat_state[sender] = "idle"

        history = chat_memory[sender]
        state = chat_state[sender]

        # =============================================
        # PESAN BARU DARI WHATSAPP (Pertama kali)
        # =============================================
        if not user_input and state == "idle":
            final_reply = f"Tuan, ada pesan masuk dari {sender_name}."
            final_reply += "\nMau saya bacakan?"

            audio_url = text_to_speech(final_reply)

            chat_memory[sender].append({"role": "assistant", "content": final_reply})
            chat_state[sender] = "waiting_read"

            return jsonify({"message": final_reply, "audio": audio_url})

        # =============================================
        # PROSES DENGAN AI
        # =============================================
        messages = [{"role": "system", "content": system_prompt}]
        messages += history[-8:]
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
                timeout=8
            )
            result = response.json()
            reply_ai = result["choices"][0]["message"]["content"] if "choices" in result else "Maaf Tuan, ada gangguan."
        except Exception as e:
            print("AI ERROR:", str(e))
            reply_ai = "Saya sedang memproses, Tuan."

        # Simpan memory
        chat_memory[sender].append({"role": "user", "content": user_input})
        chat_memory[sender].append({"role": "assistant", "content": reply_ai})

        # Update state sederhana
        text_lower = user_input.lower()
        if "ya" in text_lower or "bacakan" in text_lower:
            chat_state[sender] = "waiting_reply"
        elif "balas" in text_lower or "ya" in text_lower and chat_state[sender] == "waiting_reply":
            chat_state[sender] = "reply_mode"

        audio_url = text_to_speech(reply_ai)

        return jsonify({
            "message": reply_ai,
            "audio": audio_url,
            "state": chat_state[sender]   # Optional, bisa dipakai di Tasker
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "message": "Jarvis sedang mengalami gangguan.",
            "audio": ""
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
