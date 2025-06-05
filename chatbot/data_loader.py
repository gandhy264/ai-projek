import json
import os

# Lokasi root proyek
base_dir = os.path.dirname(os.path.dirname(__file__))
data_dir = os.path.join(base_dir, "chatbot", "data")

# Pastikan folder data ada
os.makedirs(data_dir, exist_ok=True)

# -------------------------------
# Load daftar kue
# -------------------------------
def load_daftar_kue():
    path = os.path.join(data_dir, "data_kue.json")
    with open(path, "r") as f:
        return json.load(f)

def get_nama_kue_lower(daftar_kue):
    return [kue["nama"].lower() for kue in daftar_kue]

# -------------------------------
# Load & simpan knowledge base
# -------------------------------
def load_kb(path=None):
    if path is None:
        path = os.path.join(data_dir, "knowledge_base.json")

    if os.path.exists(path):
        with open(path, "r") as f:
            kb = json.load(f)
            if "intents" not in kb:
                raise KeyError("Key 'intents' not found in knowledge_base.json")
            return kb
    raise FileNotFoundError(f"File {path} not found.")

def simpan_ke_kb(pertanyaan, jawaban, path=None):
    if path is None:
        path = os.path.join(data_dir, "knowledge_base.json")
    kb = load_kb(path)
    kb[pertanyaan] = jawaban
    with open(path, "w") as f:
        json.dump(kb, f, indent=4)

# -------------------------------
# Transaksi
# -------------------------------
def load_transaksi():
    path = os.path.join(data_dir, "transaksi.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def simpan_transaksi(transaksi_baru):
    path = os.path.join(data_dir, "transaksi.json")

    data = load_transaksi()
    data.append(transaksi_baru)

    with open(path, "w") as f:
        json.dump(data, f, indent=4)
