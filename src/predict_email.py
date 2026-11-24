import argparse
from pathlib import Path

import joblib
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "phishing_email_model.joblib"


def predict(email_text: str):
    bundle = joblib.load(MODEL_PATH)
    model = bundle["model"]
    label_encoder = bundle["label_encoder"]

    probabilities = model.predict_proba(pd.DataFrame({"email_text": [email_text]}))[0]
    prediction = model.predict(pd.DataFrame({"email_text": [email_text]}))[0]
    label = label_encoder.inverse_transform([prediction])[0]

    confidence_by_label = {
        label_encoder.inverse_transform([idx])[0]: float(prob)
        for idx, prob in enumerate(probabilities)
    }

    return label, confidence_by_label


def main():
    parser = argparse.ArgumentParser(description="Classify an email as phishing or safe.")
    parser.add_argument("email", help="Raw email text to classify")
    args = parser.parse_args()

    label, probabilities = predict(args.email)
    friendly_label = "Phishing" if label == "phishing" else "Safe"

    print(f"Prediction: {friendly_label}")
    print("Probabilities:")
    for name, score in sorted(probabilities.items()):
        print(f"  {name}: {score:.2%}")


if __name__ == "__main__":
    main()
