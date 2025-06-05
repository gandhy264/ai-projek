import os
import random
import json
import pickle
import numpy as np
import datetime

from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder

# Base directory untuk folder chatbot ini
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load intents.json dari folder data
with open(os.path.join(BASE_DIR, "intents.json"), "r", encoding="utf-8") as file:
    intents = json.load(file)

# Load model dari folder model
try:
    model = load_model(os.path.join(BASE_DIR, "model", "chatbot_model.keras"))
except ValueError as e:
    print(f"Error loading model: {e}")
    exit(1)

# Load tokenizer dan label encoder dari folder data
with open(os.path.join(BASE_DIR, "tokenizer.pickle"), "rb") as handle:
    tokenizer = pickle.load(handle)

with open(os.path.join(BASE_DIR, "label_encoder.pkl"), "rb") as enc:
    lbl_encoder = pickle.load(enc)

MAX_LEN = 20

order_state = {
    "in_progress": False,
    "items": [],
    "delivery": False,
    "name": "",
    "address": "",
    "phone": ""
}

def classify_intent(text):
    sequences = tokenizer.texts_to_sequences([text])
    padded = np.array([np.pad(seq, (0, MAX_LEN - len(seq)), mode='constant') for seq in sequences])
    prediction = model.predict(padded, verbose=0)
    intent = lbl_encoder.inverse_transform([np.argmax(prediction)])[0]
    confidence = np.max(prediction)
    return intent, confidence

def get_response(intent_name):
    for intent in intents["intents"]:
        if intent["tag"] == intent_name:
            return random.choice(intent["responses"])
    return "Maaf, saya tidak mengerti."

def format_order():
    return "\n".join(f"- {item}" for item in order_state["items"])

def generate_receipt():
    total_items = len(order_state["items"])
    total_price = total_items * 20000
    receipt = f"""
🧾 Struk Pesanan Anda:
Nama: {order_state['name']}
Nomor HP: {order_state.get('phone', 'N/A')}
Alamat: {order_state.get('address', 'N/A')}
Pesanan:
{format_order()}

Total: Rp{total_price:,.0f}
"""
    return receipt

def handle_order_flow(user_input):
    if not order_state["items"]:
        order_state["items"].append(user_input)
        return "Baik, sudah saya catat. Apakah ada pesanan lain?"
    if user_input.lower() in ["tidak", "cukup", "sudah"]:
        order_state["in_progress"] = False
        return "Pesanan Anda sudah kami catat. Untuk pengambilan atau pengantaran?"
    order_state["items"].append(user_input)
    return "Ditambahkan. Ada lagi?"

def handle_delivery_flow(user_input):
    if order_state["name"] == "":
        order_state["name"] = user_input
        return "Boleh minta nomor HP Anda?"
    elif order_state["phone"] == "":
        order_state["phone"] = user_input
        return "Alamat pengiriman ke mana ya?"
    elif order_state["address"] == "":
        order_state["address"] = user_input
        ready_time = datetime.datetime.now() + datetime.timedelta(hours=2)
        return f"Terima kasih. Pesanan akan diantar sekitar pukul {ready_time.strftime('%H:%M')}.\n" + generate_receipt()
    return "Pesanan Anda telah diproses."

def handle_pickup_flow(user_input):
    if order_state["name"] == "":
        order_state["name"] = user_input
        ready_time = datetime.datetime.now() + datetime.timedelta(hours=2)
        return f"Terima kasih. Pesanan bisa diambil sekitar pukul {ready_time.strftime('%H:%M')}.\n" + generate_receipt()
    return "Pesanan Anda telah dicatat."

def jawab_pertanyaan(user_input):
    user_input = user_input.strip().lower()

    if order_state["in_progress"]:
        return handle_order_flow(user_input)
    elif order_state["delivery"]:
        return handle_delivery_flow(user_input)
    elif order_state["items"] and not order_state["delivery"] and order_state["name"] == "":
        return handle_pickup_flow(user_input)

    intent, confidence = classify_intent(user_input)

    if confidence > 0.7:
        if intent == "order":
            order_state.update({"in_progress": True, "items": [], "name": "", "address": "", "phone": ""})
            return get_response(intent)
        elif intent == "delivery":
            order_state["delivery"] = True
            return "Baik, untuk pengiriman pesanan mohon isi data berikut.\nSiapa nama Anda?"
        elif intent == "pickup":
            order_state["delivery"] = False
            return "Baik, untuk pengambilan pesanan, siapa nama Anda?"
        else:
            return get_response(intent)
    else:
        return "Maaf, saya kurang paham maksud Anda. Bisa dijelaskan lagi?"
