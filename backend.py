from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load dataset
df = pd.read_csv(r"C:\Users\ARJAV\Desktop\New folder (4)\approx_engine_chatbot_dataset.csv")

def find_answer(user_query):
    user_query = user_query.lower()

    best_match = None

    for _, row in df.iterrows():
        question = str(row["question"]).lower()

        # simple matching logic
        if any(word in question for word in user_query.split()):
            best_match = row["answer"]
            break

    if best_match:
        return best_match

    return "I didn’t understand. Try asking about sample, count, speed, or accuracy."

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_query = data.get("message", "")

    answer = find_answer(user_query)

    return jsonify({"reply": answer})

if __name__ == "__main__":
    app.run(port=5000)