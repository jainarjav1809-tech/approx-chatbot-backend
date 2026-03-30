from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

# -------- LOAD DATASET --------
df = pd.read_csv("approx_engine_chatbot_dataset.csv", encoding="utf-8")

# -------- LOAD MODEL --------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -------- CREATE EMBEDDINGS --------
questions = df["user_query"].astype(str).tolist()
embeddings = model.encode(questions)

# -------- FUNCTION --------
def find_answer(user_query):
    query_embedding = model.encode([user_query])

    similarities = cosine_similarity(query_embedding, embeddings)[0]

    best_idx = similarities.argmax()
    best_score = similarities[best_idx]

    # threshold to avoid wrong answers
    if best_score < 0.3:
        return "I didn't understand. Try asking about SUM, COUNT, AVG, GROUP BY, etc."

    return str(df.iloc[best_idx]["notes"])

# -------- API --------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_query = data.get("message", "")

        answer = find_answer(user_query)

        return jsonify({"reply": answer})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"reply": "Server error occurred"}), 500

# -------- HEALTH --------
@app.route("/", methods=["GET"])
def home():
    return "RAG API running 🚀"

# -------- RUN --------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
