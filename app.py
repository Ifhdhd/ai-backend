from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app)

# API key dari environment (Render)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-pro")

@app.route("/")
def home():
    return "Backend jalan 🚀"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message")

    if not user_input:
        return jsonify({"error": "no input"})

    response = model.generate_content(user_input)

    return jsonify({"reply": response.text})

if __name__ == "__main__":
    app.run()
