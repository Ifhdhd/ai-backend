from flask import Flask, request, jsonify, make_response
import requests
import os

app = Flask(__name__)

# 🔥 HANDLE CORS MANUAL (LEBIH KUAT)
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@app.route("/")
def home():
    return "Backend Groq jalan 🚀"

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():

    # 🔥 WAJIB UNTUK PREFLIGHT
    if request.method == "OPTIONS":
        return make_response("", 200)

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
                {"role": "system", "content": "Kamu AI santai, jawab bahasa Indonesia."},
                {"role": "user", "content": user_input}
            ]
        }

        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers
        )

        result = res.json()

        if "error" in result:
            return jsonify({"error": result["error"]}), 500

        reply = result["choices"][0]["message"]["content"]

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run()
