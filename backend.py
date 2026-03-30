from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# -------- LOAD DATASET --------
try:
    df = pd.read_csv("approx_engine_chatbot_dataset.csv", encoding="utf-8")
    print("✅ Dataset loaded successfully")
    print(df.head())
except Exception as e:
    print("❌ ERROR LOADING DATASET:", e)
    df = pd.DataFrame()

# -------- FUNCTION --------
def find_answer(user_query):
    user_query = user_query.lower()

    for _, row in df.iterrows():
        question = str(row.get("user_query", "")).lower()
        answer = str(row.get("expected_output_type", ""))

        if any(word in question for word in user_query.split()):
            return answer

    return "I didn't understand. Try asking about sample, count, speed, or accuracy."

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

# -------- RUN --------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
