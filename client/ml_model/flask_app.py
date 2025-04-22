from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# Load the trained ML model
model = joblib.load('billing_predictor_model.pkl')


# Function to calculate the electricity bill from predicted units
def calculate_tariff(units, region_encoded):
    wheeling_charge = 1.20
    fixed_charge = 128 if region_encoded == 0 else 130  # 0 = rural, 1 = urban

    # Energy charge based on slabs
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


# Home route just for checking
@app.route('/')
def home():
    return "⚡ Electricity Bill Predictor API is running!"


# Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    try:
        # Extract input values
        region_encoded = data['region_encoded']
        year = data['year']
        month_num = data['month_num']

        # Input features for the model
        input_features = np.array([[region_encoded, year, month_num]])

        # Predict electricity units
        predicted_units = model.predict(input_features)[0]  # get scalar

        # Calculate estimated bill from predicted units
        estimated_bill = calculate_tariff(predicted_units, region_encoded)

        return jsonify({
          #  'region': 'rural' if region_encoded == 0 else 'urban',
           # 'year': year,
            #'month': month_num,
            'predicted_units_kwh': round(predicted_units, 2),
            'estimated_next_month_bill_in_inr': estimated_bill
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
