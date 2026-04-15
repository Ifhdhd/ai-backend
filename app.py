from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Backend Groq jalan 🚀"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message")

    if not user_input:
        return jsonify({"error": "no input"})

    api_key = os.getenv("GROQ_API_KEY")
    print("API KEY:", api_key)  # DEBUG

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system",
                "content": "Kamu adalah AI bebas sesuai keinginan user."
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    }

    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers
        )

        print("STATUS:", res.status_code)
        print("RESPONSE:", res.text)

        result = res.json()

        # kalau error dari Groq
        if "choices" not in result:
            return jsonify({
                "error": result
            })

        reply = result["choices"][0]["message"]["content"]

        return jsonify({
            "reply": reply
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        })

if __name__ == "__main__":
    app.run()
