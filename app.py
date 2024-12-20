from flask import Flask, render_template, request, jsonify, send_file
import os

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
    return jsonify({"response": ""})  # No automatic response

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

    # Process the uploaded file
    chat_history = []
    for line in file.stream:
        line = line.decode('utf-8').strip()
        if line.startswith("*") or line.startswith("-"):
            sender = line[0]
            message = line[2:]
            chat_history.append({"sender": sender, "message": message})
    return jsonify({"status": "success", "chat_history": chat_history})

if __name__ == "__main__":
    # Use the port assigned by Render or default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
