from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import re

app = Flask(__name__)
CORS(app)

# -------- LOAD DATASET --------
try:
    df = pd.read_csv("approx_engine_chatbot_dataset.csv", encoding="utf-8")
    print("✅ Dataset loaded")
except Exception as e:
    print("❌ Dataset load error:", e)
    df = pd.DataFrame()

# -------- TRY LOADING RAG MODEL --------
rag_enabled = False

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity

    model = SentenceTransformer("all-MiniLM-L6-v2")

    questions = df["user_query"].astype(str).tolist()
    embeddings = model.encode(questions)

    rag_enabled = True
    print("✅ RAG model loaded")

except Exception as e:
    print("❌ RAG failed, using fallback:", e)

# -------- CLEAN TEXT --------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9_ ]', '', text)
    return text

# -------- FALLBACK MATCHING --------
def fallback_answer(user_query):
    user_query = clean_text(user_query)

    stopwords = {
        "what", "is", "how", "do", "does", "the", "a", "an",
        "to", "all", "i", "am", "are", "when", "why"
    }

    query_words = [w for w in user_query.split() if w not in stopwords]

    best_match = None
    best_score = 0

    for _, row in df.iterrows():
        question = clean_text(str(row.get("user_query", "")))
        answer = str(row.get("notes", ""))

        feature = clean_text(str(row.get("command_or_feature", "")))
        focus = clean_text(str(row.get("engine_focus", "")))

        score = 0

        if user_query in question:
            score += 10

        for word in query_words:
            if word in question:
                score += 2

        for word in query_words:
            if word in feature:
                score += 4

        for word in query_words:
            if word in focus:
                score += 1

        important = ["sum", "count", "avg", "group", "sample", "error", "unexpected"]
        for word in important:
            if word in user_query and word in question:
                score += 3

        if score > best_score:
            best_score = score
            best_match = answer

    if best_match:
        return best_match

    return "I didn't understand. Try asking about SUM, COUNT, AVG, GROUP BY, SAMPLE."

# -------- MAIN ANSWER FUNCTION --------
def find_answer(user_query):
    # Try RAG first
    if rag_enabled:
        try:
            query_embedding = model.encode([user_query])
            similarities = cosine_similarity(query_embedding, embeddings)[0]

            best_idx = similarities.argmax()
            best_score = similarities[best_idx]

            if best_score > 0.3:
                return str(df.iloc[best_idx]["notes"])
        except Exception as e:
            print("❌ RAG runtime error:", e)

    # fallback
    return fallback_answer(user_query)

# -------- API --------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"reply": "No input provided"}), 400

        user_query = data.get("message", "")

        if not user_query:
            return jsonify({"reply": "Empty query"}), 400

        answer = find_answer(user_query)

        return jsonify({"reply": answer})

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"reply": "Server error occurred"}), 500

# -------- HEALTH CHECK --------
@app.route("/", methods=["GET"])
def home():
    return "API running 🚀"

# -------- RUN --------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
