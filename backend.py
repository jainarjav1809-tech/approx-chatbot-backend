from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Load dataset
df = pd.read_csv("approx_engine_chatbot_dataset.csv")

def find_answer(user_query):
    user_query = user_query.lower()

    best_match = None

    for _, row in df.iterrows():
        question = str(row["question"]).lower()

        if any(word in question for word in user_query.split()):
            best_match = row["answer"]
            break

    if best_match:
        return best_match

    return "I didn't understand. Try asking about sample, count, speed, or accuracy."

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_query = data.get("message", "")

    answer = find_answer(user_query)

    return jsonify({"reply": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
