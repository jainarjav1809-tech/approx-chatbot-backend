from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)  # ✅ Allow Botpress to call API

# -------- LOAD DATASET --------
try:
    df = pd.read_csv("approx_engine_chatbot_dataset.csv")
except Exception as e:
    print("Error loading dataset:", e)
    df = pd.DataFrame(columns=["question", "answer"])

# -------- FUNCTION TO FIND ANSWER --------
def find_answer(user_query):
    user_query = user_query.lower()

    best_match = None

    for _, row in df.iterrows():
        question = str(row["question"]).lower()

        # simple keyword match
        if any(word in question for word in user_query.split()):
            best_match = row["answer"]
            break

    if best_match:
        return best_match

    return "I didn't understand. Try asking about sample, count, speed, or accuracy."

# -------- API ROUTE --------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_query = data.get("message", "")

        answer = find_answer(user_query)

        return jsonify({"reply": answer})

    except Exception as e:
        return jsonify({"reply": "Server error occurred"}), 500

# -------- RUN APP --------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
