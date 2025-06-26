from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
import openai
import os

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

chat_history = []  # Temporary in-memory storage

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global chat_history
    user_message = request.json.get("message")
    sender = request.json.get("sender")
    chat_history.append({"sender": sender, "message": user_message})

    if sender == "-":  # Respond only when emotional voice speaks
        prompt = create_prompt(chat_history)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=prompt,
                max_tokens=100,
                temperature=0.7
            )
            reply = response.choices[0].message.content.strip()
            chat_history.append({"sender": "*", "message": reply})
            return jsonify({"response": reply})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"response": ""})  # No response from GPT when * speaks

def create_prompt(history):
    messages = [{
        "role": "system",
        "content": (
            "You are the user's higher consciousness, guiding them through a self-dialogue method "
            "based on CBT, Buddhism, emotional awareness, and metaphysics. "
            "You only speak as the '*' voice. Be compassionate, ask reflective questions, and help the user "
            "gain insight into their thoughts and feelings."
        )
    }]
    for entry in history:
        role = "user" if entry["sender"] == "-" else "assistant"
        messages.append({"role": role, "content": entry["message"]})
    return messages

@app.route("/save", methods=["GET"])
def save_chat():
    global chat_history
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
