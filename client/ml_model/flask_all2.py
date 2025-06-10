from flask import Flask, request, render_template, redirect, flash, url_for
from openai import OpenAI
import joblib
import numpy as np
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flash messages

# --- DB SETUP ---
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

with get_db_connection() as conn:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()

# --- MODEL + BILL CALC ---
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
    return round(total_energy_cost + fixed_charge, 2)

# --- CHATBOT ---
client = OpenAI()
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

# --- ROUTES ---
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password)).fetchone()
        conn.close()

        if user:
            flash("Login successful!", "success")
            return redirect("/home?user=" + email)
        else:
            flash("Invalid credentials!", "error")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            conn = get_db_connection()
            conn.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            flash("Signup successful!", "success")
        except sqlite3.IntegrityError:
            flash("Email already exists!", "error")
        return redirect("/signup")
    return render_template("signup.html")

@app.route("/home", methods=["GET", "POST"])
def home():
    user_email = request.args.get("user")

    if not user_email:
        flash("Please login first.", "error")
        return redirect("/")

    # Default usage data
    usage_data = {
        "current_month_kwh": round(np.random.uniform(180, 350), 2),
        "last_month_kwh": round(np.random.uniform(120, 250), 2),
        "predicted_next_kwh": None  # to be filled
    }

    chatbot_answer = None
    bill_result = None

    # --- Handle form POST ---
    if request.method == "POST":
        if "chat_question" in request.form:
            question = request.form["chat_question"]
            chatbot_answer = get_custom_answer(question) or get_openai_response(question)

        elif all(k in request.form for k in ("region_encoded", "year", "month_num")):
            try:
                region_encoded = int(request.form["region_encoded"])
                year = int(request.form["year"])
                month_num = int(request.form["month_num"])
                input_features = np.array([[region_encoded, year, month_num]])

                predicted_units = model.predict(input_features)[0]
                estimated_bill = calculate_tariff(predicted_units, region_encoded)

                # Update dashboard value with actual predicted usage
                usage_data["predicted_next_kwh"] = round(predicted_units, 2)

                bill_result = {
                    "predicted_units": round(predicted_units, 2),
                    "estimated_bill": round(estimated_bill, 2)
                }

            except Exception as e:
                flash(f"Prediction error: {str(e)}", "danger")

    # If still None, fallback to random
    if usage_data["predicted_next_kwh"] is None:
        usage_data["predicted_next_kwh"] = round(np.random.uniform(200, 320), 2)

    return render_template(
        "home.html",
        user_email=user_email,
        usage=usage_data,
        chatbot_answer=chatbot_answer,
        bill_result=bill_result
    )


# --- RUN ---
if __name__ == "__main__":
    app.run(debug=True)
