import os
import json
import re
from datetime import datetime
from fuzzywuzzy import process

# ----------------------------------------
# Stopword umum untuk penghapusan
# ----------------------------------------
STOPWORDS = {
    "saya", "ingin", "mau", "tolong", "bisa", "apakah", "ada", "yang",
    "berapa", "harga", "di", "ke", "dengan", "dan", "kue", "ya", "kah",
    "apa", "itu", "dong", "nih", "aku", "kamu", "beli", "pesan"
}

# ----------------------------------------
# Fungsi: Normalisasi teks (huruf kecil, hapus simbol)
# ----------------------------------------
def normalisasi_teks(teks):
    teks = teks.lower()
    teks = re.sub(r'[^\w\s]', '', teks)  # hapus tanda baca
    teks = re.sub(r'\s+', ' ', teks)     # hapus spasi berlebih
    return teks.strip()

# ----------------------------------------
# Fungsi: Hapus stopwords dari teks
# ----------------------------------------
def hapus_stopwords(teks):
    kata = teks.split()
    hasil = [k for k in kata if k not in STOPWORDS]
    return ' '.join(hasil)

# ----------------------------------------
# Fungsi: Koreksi typo menggunakan fuzzy matching
# ----------------------------------------
def koreksi_typo(teks, daftar_kata):
    kata_input = teks.split()
    hasil = []
    for kata in kata_input:
        match, skor = process.extractOne(kata, daftar_kata)
        hasil.append(match if skor >= 80 else kata)
    return ' '.join(hasil)

# ----------------------------------------
# Fungsi: Proses pembersihan input lengkap
# ----------------------------------------
def bersihkan_input(teks, daftar_kata_valid=None):
    teks = normalisasi_teks(teks)
    teks = hapus_stopwords(teks)
    if daftar_kata_valid:
        teks = koreksi_typo(teks, daftar_kata_valid)
    return teks

# ----------------------------------------
# Fungsi: Memberi sapaan otomatis sesuai waktu
# ----------------------------------------
def sapaan_sesuai_waktu():
    jam = datetime.now().hour
    if 4 <= jam < 11:
        waktu = "Selamat pagi"
    elif 11 <= jam < 15:
        waktu = "Selamat siang"
    elif 15 <= jam < 18:
        waktu = "Selamat sore"
    else:
        waktu = "Selamat malam"
    return f"{waktu}! Selamat datang di Toko Kue Kami. Ada yang bisa saya bantu?"

# ----------------------------------------
# Fungsi: Menyimpan riwayat chat
# ----------------------------------------
def simpan_riwayat_chat(user_input, bot_response, file_path="data/chat_history.json"):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    riwayat = {
        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user_input,
        "bot": bot_response
    }
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        data = []
    data.append(riwayat)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# ----------------------------------------
# Fungsi: Mencari nama kue terdekat
# ----------------------------------------
def cari_kue_terdekat(nama_input, daftar_nama_kue, daftar_kue):
    if not nama_input or not daftar_nama_kue:
        return "Maaf, daftar kue sedang tidak tersedia."
    try:
        match, skor = process.extractOne(nama_input, daftar_nama_kue)
    except Exception:
        return "Maaf, terjadi kesalahan saat mencari nama kue."
    if skor >= 70:
        for kue in daftar_kue:
            if kue["nama"].lower() == match.lower():
                return f"Apakah maksud Anda '{kue['nama']}'? Harganya Rp{kue['harga']}"
    return "Maaf, kami tidak menemukan kue yang dimaksud. Bisa ditulis ulang?"

# ----------------------------------------
# Fungsi: Format waktu singkat (jam:menit)
# ----------------------------------------
def waktu_singkat():
    return datetime.now().strftime("%H:%M")

# ----------------------------------------
# Fungsi: Log pertanyaan tidak dikenali
# ----------------------------------------
def log_pertanyaan_tidak_dikenal(pertanyaan, file_path="data/unrecognized.json"):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    entry = {
        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pertanyaan": pertanyaan
    }
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        data = []
    data.append(entry)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# ----------------------------------------
# Fungsi: Ambil log pertanyaan tidak dikenali
# ----------------------------------------
def ambil_log_pertanyaan_tidak_dikenal(file_path="data/unrecognized.json"):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return []

# ----------------------------------------
# Fungsi: Hapus log pertanyaan tidak dikenali
# ----------------------------------------
def hapus_log_pertanyaan_tidak_dikenal(file_path="data/unrecognized.json"):
    if os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump([], f)
