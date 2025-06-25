from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
import os
import openai

app = Flask(__name__)
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
chat_history = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global chat_history
    user_message = request.json.get("message")
    sender = request.json.get("sender")

    chat_history.append({"sender": sender, "message": user_message})

    response_text = ""
    if sender == "?":  # You can change this condition
        messages = [{"role": "system", "content": "You are a compassionate dialogue guide helping someone reflect."}]
        for entry in chat_history:
            messages.append({
                "role": "user" if entry["sender"] == "*" else "assistant",
                "content": entry["message"]
            })
        try:
            gpt_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150
            )
            response_text = gpt_response.choices[0].message['content'].strip()
            chat_history.append({"sender": "*", "message": response_text})
        except Exception as e:
            response_text = "Error connecting to GPT: " + str(e)

    return jsonify({"response": response_text})

@app.route("/save", methods=["GET"])
def save_chat():
    file_path = "chat_history.txt"
    with open(file_path, "w") as f:
        for entry in chat_history:
            f.write(f"{entry['sender']} {entry['message']}\n")
    return send_file(file_path, as_attachment=True)

@app.route("/load", methods=["POST"])
def load_chat():
    global chat_history
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    chat_history = []
    for line in file.stream:
        line = line.decode('utf-8').strip()
        if line.startswith("*") or line.startswith("-"):
            sender = line[0]
            message = line[2:]
            chat_history.append({"sender": sender, "message": message})
    return jsonify({"status": "success", "chat_history": chat_history})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
