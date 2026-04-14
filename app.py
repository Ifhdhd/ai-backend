from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(name)
CORS(app)  # biar frontend bisa akses

ambil API key dari environment (AMAN)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

model = genai.GenerativeModel(
model_name="gemini-pro",
system_instruction="Kamu adalah AI pribadi milik user. Kamu fleksibel, santai, dan mengikuti gaya bicara user. Jawaban harus natural seperti manusia."
)

chat = model.start_chat(history=[])

@app.route("/")
def home():
return "AI Backend Jalan 🚀"

@app.route("/chat", methods=["POST"])
def chat_api():
try:
data = request.get_json()
user_input = data.get("message")

    response = chat.send_message(user_input)
    reply = response.text

    return jsonify({"reply": reply})

except Exception as e:
    return jsonify({"error": str(e)}), 500

if name == "main":
app.run(host="0.0.0.0", port=10000)