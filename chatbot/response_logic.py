import random
import json
import numpy as np
from tensorflow.keras.models import load_model
import pickle
from datetime import datetime, timedelta

from rapidfuzz import process
from chatbot.data_loader import (
    load_daftar_kue, load_kb, simpan_transaksi,
    get_nama_kue_lower, load_transaksi
)
from chatbot.utils import (
    bersihkan_input, cari_kue_terdekat, log_pertanyaan_tidak_dikenal
)

# Load data & model
daftar_kue = load_daftar_kue()
knowledge_base = load_kb()
nama_kue = get_nama_kue_lower(daftar_kue)

model = load_model("chatbot/data/model/chatbot_model.keras")
with open("chatbot/data/words.pkl", "rb") as f: 
    words = pickle.load(f)
with open("chatbot/data/label_encoder.pkl", "rb") as f: 
    lbl_encoder = pickle.load(f)
with open("chatbot/intents.json") as f: 
    intents = json.load(f)

session = {
    "tahap": None,
    "pesanan": {},
    "konfirmasi": {}
}

def cari_response_intent(tag):
    for intent in intents["intents"]:
        if intent["tag"] == tag:
            return random.choice(intent["responses"])
    return None

def prediksi_intent_ml(pesan):
    from nltk.stem import WordNetLemmatizer
    from nltk.tokenize import word_tokenize
    lemmatizer = WordNetLemmatizer()

    tokens = word_tokenize(pesan.lower())
    tokens = [lemmatizer.lemmatize(w) for w in tokens]

    bag = [1 if w in tokens else 0 for w in words]
    input_data = np.array([bag])

    hasil = model.predict(input_data, verbose=0)[0]
    idx = np.argmax(hasil)
    tag = lbl_encoder.inverse_transform([idx])[0]
    confidence = hasil[idx]

    if confidence >= 0.75:
        return cari_response_intent(tag)
    return None

def proses_input_user(pesan, daftar_kue=daftar_kue, nama_kue=nama_kue, knowledge_base=knowledge_base):
    pesan_asli = pesan
    pesan_bersih = bersihkan_input(pesan, daftar_kata_valid=nama_kue)

    # Multi-step: Nama
    if session["tahap"] == "tanya_nama":
        session["konfirmasi"]["nama"] = pesan_asli
        if session["konfirmasi"]["metode"] == "ambil":
            waktu_ambil = (datetime.now() + timedelta(hours=2)).strftime("%H:%M")
            nota = cari_response_intent("konfirmasi_ambil").replace("{nama}", session["konfirmasi"]["nama"]).replace("{waktu}", waktu_ambil)
            session["tahap"] = None
            simpan_transaksi({
                "nama_kue": session["pesanan"]["nama_kue"],
                "jumlah": session["pesanan"]["jumlah"],
                "metode": session["konfirmasi"]["metode"],
                "nama": session["konfirmasi"]["nama"],
                "hp": "",
                "alamat": "",
                "tanggal_ambil": datetime.now().strftime("%d-%m-%Y %H:%M")
            })
            return nota, True
        else:
            session["tahap"] = "tanya_hp"
            return cari_response_intent("tanya_hp"), True

    # Multi-step: HP
    if session["tahap"] == "tanya_hp":
        session["konfirmasi"]["hp"] = pesan_asli
        session["tahap"] = "tanya_alamat"
        return cari_response_intent("tanya_alamat"), True

    # Multi-step: Alamat
    if session["tahap"] == "tanya_alamat":
        session["konfirmasi"]["alamat"] = pesan_asli
        nama = session["konfirmasi"]["nama"]
        waktu_kirim = (datetime.now() + timedelta(hours=2)).strftime("%H:%M")
        nota_template = cari_response_intent("konfirmasi_kirim")
        nota = nota_template.replace("{nama}", nama).replace("{alamat}", session["konfirmasi"]["alamat"]).replace("{waktu}", waktu_kirim)
        simpan_transaksi({
            "nama_kue": session["pesanan"]["nama_kue"],
            "jumlah": session["pesanan"]["jumlah"],
            "metode": session["konfirmasi"]["metode"],
            "nama": session["konfirmasi"]["nama"],
            "hp": session["konfirmasi"]["hp"],
            "alamat": session["konfirmasi"]["alamat"],
            "tanggal_ambil": datetime.now().strftime("%d-%m-%Y %H:%M")
        })
        session["tahap"] = None
        return nota, True

    # Deteksi pemesanan
    if "pesan" in pesan_bersih:
        for kue in daftar_kue:
            if kue["nama"].lower() in pesan_bersih:
                jumlah = 1
                for kata in pesan_bersih.split():
                    if kata.isdigit():
                        jumlah = int(kata)
                        break
                session["pesanan"] = {"nama_kue": kue["nama"], "jumlah": jumlah}
                session["tahap"] = "tanya_metode"
                tanya_metode = cari_response_intent("tanya_metode").replace("{jumlah}", str(jumlah)).replace("{nama_kue}", kue["nama"])
                return tanya_metode, True
        return cari_response_intent("tanya_kue"), True

    # Pilihan metode (ambil/kirim)
    if session["tahap"] == "tanya_metode":
        if "ambil" in pesan_bersih:
            session["konfirmasi"]["metode"] = "ambil"
        elif "kirim" in pesan_bersih or "antar" in pesan_bersih:
            session["konfirmasi"]["metode"] = "kirim"
        else:
            return cari_response_intent("tanya_metode_ulang"), True
        session["tahap"] = "tanya_nama"
        return cari_response_intent("tanya_nama"), True

    # Coba prediksi intent dengan model ML
    jawaban_ml = prediksi_intent_ml(pesan_bersih)
    if jawaban_ml:
        return jawaban_ml, True

    # Fallback
    return cari_response_intent("fallback") or "Maaf, saya kurang mengerti. Bisa ulangi dengan kata lain?", False
