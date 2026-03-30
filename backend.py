from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# -------- LOAD DATASET --------
try:
    df = pd.read_csv("approx_engine_chatbot_dataset.csv", encoding="utf-8")
    print("✅ Dataset loaded")
except Exception as e:
    print("❌ ERROR LOADING DATASET:", e)
    df = pd.DataFrame()

# -------- FUNCTION --------
def find_answer(user_query):
    user_query = user_query.lower().strip()

    # remove useless words
    stopwords = {"what", "is", "how", "do", "does", "the", "a", "an", "to", "all", "i"}
    query_words = [word for word in user_query.split() if word not in stopwords]

    best_match = None
    best_score = 0

    for _, row in df.iterrows():
        question = str(row.get("user_query", "")).lower()
        answer = str(row.get("notes", ""))
        feature = str(row.get("command_or_feature", "")).lower()
        focus = str(row.get("engine_focus", "")).lower()

        score = 0

        # 1. keyword match in question
        for word in query_words:
            if word in question:
                score += 2

        # 2. feature match (VERY IMPORTANT)
        for word in query_words:
            if word in feature:
                score += 3

        # 3. engine focus match
        for word in query_words:
            if word in focus:
                score += 1

        if score > best_score:
            best_score = score
            best_match = answer

    if best_match and best_score > 0:
        return best_match

    return "I didn't understand. Try asking about sample, count, sum, avg, or group by."

# -------- API --------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_query = data.get("message", "")

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
