from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
from openai import OpenAI
import os

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
            response = client.chat.completions.create(
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

    return jsonify({"response": ""})  # No GPT response when * speaks


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


@app.route("/guide")
def guide():
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a gentle and helpful coach."},
                {"role": "user", "content": "Please provide a guiding message to help someone stuck in their self-dialogue."}
            ]
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
