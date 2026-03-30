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
    print("❌ ERROR LOADING DATASET:", e)
    df = pd.DataFrame()

# -------- TEXT CLEANING --------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9_ ]', '', text)  # remove symbols
    return text

# -------- FUNCTION --------
def find_answer(user_query):
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

        # 1. exact phrase match (VERY STRONG)
        if user_query in question:
            score += 10

        # 2. keyword overlap
        for word in query_words:
            if word in question:
                score += 2

        # 3. feature match (COUNT, SUM, AVG, etc.)
        for word in query_words:
            if word in feature:
                score += 4

        # 4. engine focus (approx/exact)
        for word in query_words:
            if word in focus:
                score += 1

        # 5. boost important keywords
        important = ["sum", "count", "avg", "group", "sample", "error", "unexpected"]
        for word in important:
            if word in user_query and word in question:
                score += 3

        if score > best_score:
            best_score = score
            best_match = answer

    if best_match and best_score > 0:
        return best_match

    return "I didn't understand. Try asking about SUM, COUNT, AVG, GROUP BY, SAMPLE, or errors."

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
    return "API is running 🚀"

# -------- RUN --------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
