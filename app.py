from flask import Flask, render_template, request, jsonify
import pickle
import random
import os
import psycopg2

app = Flask(__name__)

# ================= LOAD AI MODEL =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "chatbot_model.pkl")
with open(MODEL_PATH, "rb") as f:
    vectorizer, model = pickle.load(f)

# ================= DATABASE (RENDER POSTGRES) =================
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_PORT = os.environ.get("DB_PORT", "5432")

conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    port=DB_PORT
)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    name TEXT,
    date TEXT,
    time TEXT
)
""")
conn.commit()

# ================= APPOINTMENT STATE =================
appointment_state = {
    "step": None,   # None | name | date | time
    "name": "",
    "date": ""
}

# ================= RESPONSES =================
responses = {
    "greeting": [
        "Hello 😊 I’m your hospital virtual assistant. How can I help you?",
        "Hi 👋 Welcome to our hospital. How may I assist you today?"
    ],
    "doctor": [
        "👨‍⚕️ Doctors are available from 9 AM to 5 PM."
    ],
    "timings": [
        "⏰ Hospital visiting hours are from 10 AM to 7 PM."
    ],
    "billing": [
        "💳 Billing counter is located near the main reception."
    ],
    "insurance": [
        "🛡️ Insurance desk assists with all health insurance claims."
    ],
    "lab_reports": [
        "🧪 Lab reports can be collected from the diagnostics department."
    ],
    "pharmacy": [
        "💊 Pharmacy is open 24/7 on the ground floor."
    ],
    "emergency": [
        "🚨 Emergency services are available 24/7."
    ],
    "thanks": [
        "You’re welcome 😊 Stay healthy!"
    ],
    "bye": [
        "Goodbye 👋 Take care!"
    ]
}

# ================= CHATBOT LOGIC =================
def chatbot_reply(message):
    message = message.strip().lower()

    # -------- APPOINTMENT FLOW --------
    if appointment_state["step"] == "time":
        time = message
        name = appointment_state["name"]
        date = appointment_state["date"]

        cur.execute(
            "INSERT INTO appointments (name, date, time) VALUES (%s, %s, %s)",
            (name, date, time)
        )
        conn.commit()

        appointment_state.update({"step": None, "name": "", "date": ""})

        return f"✅ Appointment booked for **{name}** on **{date}** at **{time}**."

    if appointment_state["step"] == "date":
        appointment_state["date"] = message
        appointment_state["step"] = "time"
        return "⏰ Please tell your preferred appointment time."

    if appointment_state["step"] == "name":
        appointment_state["name"] = message
        appointment_state["step"] = "date"
        return "📅 Please tell your preferred appointment date (DD-MM-YYYY)."

    # -------- KEYWORDS --------
    if "thank" in message:
        return random.choice(responses["thanks"])
    if "bye" in message:
        return random.choice(responses["bye"])
    if "billing" in message:
        return random.choice(responses["billing"])
    if "insurance" in message:
        return random.choice(responses["insurance"])
    if "lab" in message:
        return random.choice(responses["lab_reports"])
    if "emergency" in message:
        return random.choice(responses["emergency"])
    if "doctor" in message:
        return random.choice(responses["doctor"])
    if "pharmacy" in message:
        return random.choice(responses["pharmacy"])

    # -------- AI INTENT --------
    X = vectorizer.transform([message])
    intent = model.predict(X)[0]

    if intent == "appointment":
        appointment_state["step"] = "name"
        return "📝 Please tell your name to book an appointment."

    if intent in responses:
        return random.choice(responses[intent])

    return "❓ Sorry, I didn’t understand your query."

# ================= ROUTES =================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    reply = chatbot_reply(data.get("message", ""))
    return jsonify({"reply": reply})

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
