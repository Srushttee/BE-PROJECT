from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
import joblib
import numpy as np
app = Flask(__name__)

# ------------------ OpenAI Chatbot Setup ------------------ #
#openai.api_key = os.getenv("OPENAI_API_KEY")  # Use environment variable for safety
client = OpenAI()
# Custom Q&A
custom_qa = {
    "what is your name?": "I'm your custom chatbot!",
    "how can I reset my password?": "Click on 'Forgot Password' at the login page."
}

def get_custom_answer(question):
    return custom_qa.get(question.lower())

def get_openai_response(question):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_question = data.get("question", "").strip()

    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    # Try custom Q&A
    answer = get_custom_answer(user_question)

    # Fallback to OpenAI
    if not answer:
        answer = get_openai_response(user_question)

    return jsonify({"answer": answer})
# ------------------ Electricity Bill Predictor Setup ------------------ #
model = joblib.load('billing_predictor_model.pkl')

def calculate_tariff(units, region_encoded):
    wheeling_charge = 1.20
    fixed_charge = 128 if region_encoded == 0 else 130

    if units <= 100:
        energy_charge = 5.32
    elif units <= 300:
        energy_charge = 10.82
    elif units <= 500:
        energy_charge = 14.64
    else:
        energy_charge = 16.45

    total_energy_cost = units * (energy_charge + wheeling_charge)
    total_bill = round(total_energy_cost + fixed_charge, 2)
    return total_bill

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    try:
        region_encoded = data['region_encoded']
        year = data['year']
        month_num = data['month_num']
        input_features = np.array([[region_encoded, year, month_num]])

        predicted_units = model.predict(input_features)[0]
        estimated_bill = calculate_tariff(predicted_units, region_encoded)

        return jsonify({
            'predicted_units_kwh': round(predicted_units, 2),
            'estimated_next_month_bill_in_inr': estimated_bill
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ------------------ Home Route ------------------ #
@app.route("/")
def home():
    return " Chatbot &  Electricity Bill Predictor API are running!"


# ------------------ Run the App ------------------ #
if __name__ == "__main__":
    app.run(debug=True)
