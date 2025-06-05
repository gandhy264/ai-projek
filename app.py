from flask import Flask, render_template, request, jsonify
from chatbot.chatbot import jawab_pertanyaan

app = Flask(__name__)

# ---------------------------
# Halaman utama
# ---------------------------
@app.route('/')
def index():
    # Hanya menampilkan halaman HTML (chat UI)
    return render_template('index.html')

# ---------------------------
# Endpoint chat (AJAX)
# ---------------------------
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({'reply': "Maaf, saya tidak menerima pesan apa pun."})

    bot_reply = jawab_pertanyaan(user_message)
    return jsonify({'reply': bot_reply})

# ---------------------------
# Jalankan server Flask
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
