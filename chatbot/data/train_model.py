import json
import pickle
import numpy as np
import os
import nltk
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

# Pastikan resource NLTK sudah ada, kalau belum download
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Stopwords bahasa Indonesia
try:
    stop_words = set(stopwords.words('indonesian'))
except LookupError:
    # Jika stopwords indonesian tidak tersedia, bisa pakai list minimal
    stop_words = set([
        'yang', 'dan', 'di', 'ke', 'dari', 'ini', 'itu', 'untuk', 'pada', 'dengan', 'sebagai', 'akan',
        # tambah stopwords lain sesuai kebutuhan
    ])

# Direktori dasar dan lokasi file
BASE_DIR = os.path.dirname(__file__)
CHATBOT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

# Load file intents.json
with open(os.path.join(CHATBOT_DIR, 'intents.json'), 'r', encoding='utf-8') as f:
    intents = json.load(f)

all_words = []
tags = []
documents = []

def clean_sentence(sentence):
    """Tokenize, lowercase, dan hapus stopwords dari kalimat"""
    tokens = word_tokenize(sentence.lower())
    # Gunakan isalpha() untuk hanya kata
    filtered = [w for w in tokens if w.isalpha() and w not in stop_words]
    return filtered

# Preprocessing: ambil kata, tag, dan dokumen
for intent in intents['intents']:
    tag = intent.get('tag')
    if tag is None:
        continue
    for pattern in intent.get('patterns', []):
        words = clean_sentence(pattern)
        if not words:
            continue
        all_words.extend(words)
        documents.append((words, tag))
    if tag not in tags:
        tags.append(tag)

# Unik dan sorting kata dan tag
all_words = sorted(set(all_words))
tags = sorted(set(tags))

# Simpan words dan tags ke file pickle
with open(os.path.join(CHATBOT_DIR, 'words.pkl'), 'wb') as f:
    pickle.dump(all_words, f)
with open(os.path.join(CHATBOT_DIR, 'tags.pkl'), 'wb') as f:
    pickle.dump(tags, f)

# Buat fitur bag of words dan label
training_sentences = []
training_labels = []

for (words, label) in documents:
    word_set = set(words)
    bag = [1 if w in word_set else 0 for w in all_words]
    training_sentences.append(bag)
    training_labels.append(label)

# Encode label string ke integer
label_encoder = LabelEncoder()
training_labels_encoded = label_encoder.fit_transform(training_labels)

# Simpan label encoder
with open(os.path.join(CHATBOT_DIR, 'label_encoder.pkl'), 'wb') as f:
    pickle.dump(label_encoder, f)

# Konversi ke numpy array
X = np.array(training_sentences)
y = np.array(training_labels_encoded)

# Definisikan model Sequential
model = Sequential([
    Dense(128, input_shape=(X.shape[1],), activation='relu'),
    Dropout(0.5),
    Dense(64, activation='relu'),
    Dropout(0.3),
    Dense(len(tags), activation='softmax')
])

# Compile model
model.compile(loss='sparse_categorical_crossentropy',
              optimizer=Adam(learning_rate=0.001),
              metrics=['accuracy'])

# EarlyStopping untuk hentikan training jika loss tidak membaik
early_stop = EarlyStopping(monitor='loss', patience=10, verbose=1, restore_best_weights=True)

# Training model
model.fit(X, y, epochs=200, batch_size=8, verbose=1, callbacks=[early_stop])

# Simpan model
MODEL_PATH = os.path.join(CHATBOT_DIR, 'chatbot_model.keras')
model.save(MODEL_PATH)

print("✅ Model selesai dilatih dan disimpan di:", MODEL_PATH)
