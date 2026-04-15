from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app, origins="*")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@app.route("/")
def home():
    return "Backend Groq jalan 🚀"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("message")

        if not user_input:
            return jsonify({"error": "no input"}), 400

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {
                    "role": "system",
                    "content": "Kamu adalah AI santai, jawab bahasa Indonesia."
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        }

        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers
        )

        print("STATUS:", res.status_code)
        print("RESPONSE:", res.text)

        result = res.json()

        # 🔥 AMAN: cek error dulu
        if "error" in result:
            return jsonify({"error": result["error"]}), 500

        reply = result["choices"][0]["message"]["content"]

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
