from flask import Flask, render_template, request, jsonify
import pickle
import sqlite3
import random
import os

app = Flask(__name__)

# ================= LOAD AI MODEL =================
with open("chatbot_model.pkl", "rb") as f:
    vectorizer, model = pickle.load(f)

# ================= DATABASE (RENDER SAFE) =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "appointments.db")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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

# ================= MULTIPLE RESPONSES =================
responses = {
    "greeting": [
        "Hello 😊 I’m your hospital virtual assistant. How can I help you?",
        "Hi 👋 Welcome to our hospital. How may I assist you today?",
        "Hello! 😊 Please tell me how I can help you."
    ],
    "how_are_you": [
        "I’m doing great 😊 Thanks for asking!",
        "I’m good 😊 How can I help you today?"
    ],
    "doctor": [
        "👨‍⚕️ Doctors are available from 9 AM to 5 PM.",
        "🩺 Please tell me which department doctor you are looking for."
    ],
    "timings": [
        "⏰ Hospital visiting hours are from 10 AM to 7 PM."
    ],
    "billing": [
        "💳 Billing counter is located near the main reception.",
        "💰 Please visit the billing desk beside OPD."
    ],
    "insurance": [
        "🛡️ Insurance desk assists with all health insurance claims.",
        "📄 Please contact the insurance help desk near reception."
    ],
    "lab_reports": [
        "🧪 Lab reports can be collected from the diagnostics department.",
        "📑 Test results are available at the lab counter."
    ],
    "pharmacy": [
        "💊 Pharmacy is open 24/7 on the ground floor."
    ],
    "icu": [
        "🏥 ICU is available with 24/7 monitoring."
    ],
    "ambulance": [
        "🚑 Ambulance service is available 24/7."
    ],
    "emergency": [
        "🚨 Emergency services are available 24/7. Please go to emergency ward immediately."
    ],
    "thanks": [
        "You’re welcome 😊 Stay healthy!",
        "Happy to help 😊 Take care!"
    ],
    "bye": [
        "Goodbye 👋 Take care!",
        "Bye 😊 Wishing you good health!"
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
            "INSERT INTO appointments (name, date, time) VALUES (?, ?, ?)",
            (name, date, time)
        )
        conn.commit()

        appointment_state.update({"step": None, "name": "", "date": ""})

        return f"✅ Appointment successfully booked for **{name}** on **{date}** at **{time}**."

    if appointment_state["step"] == "date":
        appointment_state["date"] = message
        appointment_state["step"] = "time"
        return "⏰ Please tell your preferred appointment time."

    if appointment_state["step"] == "name":
        appointment_state["name"] = message
        appointment_state["step"] = "date"
        return "📅 Please tell your preferred appointment date (DD-MM-YYYY)."

    # -------- KEYWORD OVERRIDE --------
    for key in ["thanks", "thank you"]:
        if key in message:
            return random.choice(responses["thanks"])

    if "bye" in message:
        return random.choice(responses["bye"])
    if "billing" in message:
        return random.choice(responses["billing"])
    if "insurance" in message:
        return random.choice(responses["insurance"])
    if "lab" in message or "report" in message:
        return random.choice(responses["lab_reports"])
    if "emergency" in message:
        return random.choice(responses["emergency"])
    if "doctor" in message:
        return random.choice(responses["doctor"])
    if "pharmacy" in message:
        return random.choice(responses["pharmacy"])
    if "icu" in message:
        return random.choice(responses["icu"])
    if "ambulance" in message:
        return random.choice(responses["ambulance"])

    # -------- AI INTENT --------
    X = vectorizer.transform([message])
    intent = model.predict(X)[0]

    if intent == "appointment":
        appointment_state["step"] = "name"
        return "📝 Please tell your name to book an appointment."

    if intent in responses:
        return random.choice(responses[intent])

    return "❓ Sorry, I didn’t understand your query. Please try again."

# ================= ROUTES =================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    reply = chatbot_reply(data.get("message", ""))
    return jsonify({"reply": reply})

# ================= RUN (RENDER COMPATIBLE) =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
