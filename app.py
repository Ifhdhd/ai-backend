from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app, origins="*")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API KEY TIDAK ADA DI ENV")
else:
    genai.configure(api_key=api_key)

# GANTI MODEL (INI YANG STABIL)
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/")
def home():
    return "Backend jalan 🚀"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("message")

        print("INPUT:", user_input)

        if not user_input:
            return jsonify({"error": "no input"}), 400

        response = model.generate_content(user_input)

        return jsonify({"reply": response.text})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
