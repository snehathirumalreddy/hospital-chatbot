import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

texts = [
    "hi", "hello", "hey",
    "how are you",
    "book appointment", "take appointment",
    "doctor available",
    "emergency help",
    "hospital timings",
    "billing details",
    "insurance claim",
    "lab report",
    "pharmacy",
    "icu",
    "ambulance",
    "telugu lo matladu",
    "thanks",
    "bye"
]

labels = [
    "greeting", "greeting", "greeting",
    "how_are_you",
    "appointment", "appointment",
    "doctor",
    "emergency",
    "timings",
    "billing",
    "insurance",
    "lab_reports",
    "pharmacy",
    "icu",
    "ambulance",
    "telugu",
    "thanks",
    "bye"
]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

model = LogisticRegression()
model.fit(X, labels)

with open("chatbot_model.pkl", "wb") as f:
    pickle.dump((vectorizer, model), f)

print("✅ AI model trained with all intents")
