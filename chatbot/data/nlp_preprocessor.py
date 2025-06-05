import json
import os
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Inisialisasi stemmer Bahasa Indonesia
factory = StemmerFactory()
stemmer = factory.create_stemmer()

# Fungsi bantu: tokenize & stem
def tokenize_stem(sentence):
    tokens = sentence.lower().split()
    return [stemmer.stem(word) for word in tokens]

# Load data intents.json
with open('chatbot/data/intents.json', 'r', encoding='utf-8') as f:
    intents = json.load(f)

all_words = []
tags = []
xy = []

# Proses setiap pattern dalam intents
for intent in intents['intents']:
    tag = intent['tag']
    tags.append(tag)
    for pattern in intent['patterns']:
        w = tokenize_stem(pattern)
        all_words.extend(w)
        xy.append((w, tag))

# Buang duplikat dan urutkan
all_words = sorted(set(all_words))
tags = sorted(set(tags))

# Simpan list kosakata dan tag
with open('chatbot/data/words.pkl', 'wb') as f:
    pickle.dump(all_words, f)

with open('chatbot/data/tags.pkl', 'wb') as f:
    pickle.dump(tags, f)

# Encode label
le = LabelEncoder()
le.fit(tags)
with open('chatbot/data/label_encoder.pkl', 'wb') as f:
    pickle.dump(le, f)

# Fungsi bag-of-words
def bag_of_words(tokenized_sentence, all_words):
    bag = np.zeros(len(all_words), dtype=np.float32)
    for w in tokenized_sentence:
        if w in all_words:
            idx = all_words.index(w)
            bag[idx] = 1.0
    return bag

# Buat dataset X dan y
X = []
y = []

for (pattern_sentence, tag) in xy:
    bag = bag_of_words(pattern_sentence, all_words)
    X.append(bag)
    y.append(le.transform([tag])[0])  # label jadi angka

X = np.array(X)
y = np.array(y)

# Simpan ke file
np.save('chatbot/data/X.npy', X)
np.save('chatbot/data/y.npy', y)

# ✅ Tambahan: Simpan dalam 1 file intent_vectors.pkl
with open("chatbot/data/intent_vectors.pkl", "wb") as f:
    pickle.dump((X, y), f)

print("✅ Data preprocessing selesai! Semua file disimpan di chatbot/data/")
