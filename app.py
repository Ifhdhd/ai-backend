@app.route("/chat", methods=["GET", "POST"])
def chat():
    try:
        # ✅ Handle GET (biar gak "not allowed")
        if request.method == "GET":
            return "CHAT READY ✅"

        data = request.get_json(force=True)

        print("DATA MASUK:", data)

        user_input = data.get("message", "")
        history = data.get("history", [])

        if not user_input:
            return jsonify({"reply": "..."})  # jangan error, biar gak fail

        # Susun messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]

        for msg in history:
            messages.append(msg)

        messages.append({
            "role": "user",
            "content": user_input
        })

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 150
            },
            timeout=10  # ⬅️ penting biar gak timeout
        )

        result = response.json()

        if "choices" not in result:
            print("ERROR GROQ:", result)
            return jsonify({"reply": "Lagi error bentar"})  # jangan kirim error mentah

        reply = result["choices"][0]["message"]["content"]

        return jsonify({
            "reply": reply
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "reply": "Server lagi sibuk"
        })
