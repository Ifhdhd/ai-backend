from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(name)
CORS(app)

#API KEY dari environment

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-pro")

@app.route("/")
def home():
return "Backend jalan 🚀"

@app.route("/chat", methods=["POST"])
def chat():
data = request.get_json()
user_input = data.get("message")

try:
    response = model.generate_content(user_input)
    reply = response.text
    return jsonify({"reply": reply})
except Exception as e:
    return jsonify({"error": str(e)})

if name == "main":
app.run()
