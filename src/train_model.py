import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "phishing_email_matplotlib"))

import joblib
import matplotlib
import pandas as pd
import seaborn as sns
from src.email_features import EmailFeatureExtractor
from sklearn.compose import ColumnTransformer
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC

matplotlib.use("Agg")
import matplotlib.pyplot as plt


CURATED_DATA_PATH = ROOT / "data" / "training_emails.csv"
DATA_PATH = CURATED_DATA_PATH if CURATED_DATA_PATH.exists() else ROOT / "data" / "sample_emails.csv"
MODEL_PATH = ROOT / "models" / "phishing_email_model.joblib"
MATRIX_PATH = ROOT / "models" / "confusion_matrix.png"
REPORT_PATH = ROOT / "models" / "metrics_report.txt"


def build_pipeline():
    features = ColumnTransformer(
        transformers=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    ngram_range=(1, 2),
                    max_features=1500,
                ),
                "email_text",
            ),
            ("manual_features", EmailFeatureExtractor(), "email_text"),
        ],
        remainder="drop",
    )

    return Pipeline(
        steps=[
            ("features", features),
            (
                "classifier",
                CalibratedClassifierCV(
                    LinearSVC(
                        class_weight="balanced",
                        dual="auto",
                        max_iter=100000,
                        random_state=42,
                        tol=1e-3,
                    ),
                    cv=3,
                    method="sigmoid",
                    ensemble=False,
                ),
            ),
        ]
    )


def save_confusion_matrix(y_true, y_pred, labels):
    matrix = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
    )
    plt.title("Phishing Email Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig(MATRIX_PATH, dpi=160)
    plt.close()


def main():
    df = pd.read_csv(DATA_PATH)
    if not {"label", "email_text"}.issubset(df.columns):
        raise ValueError("Dataset must contain 'label' and 'email_text' columns.")

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df["label"])

    X_train, X_test, y_train, y_test = train_test_split(
        df[["email_text"]],
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    model = build_pipeline()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    class_names = list(label_encoder.classes_)

    save_confusion_matrix(y_test, predictions, class_names)

    report = classification_report(y_test, predictions, target_names=class_names)
    output = (
        f"Dataset: {DATA_PATH.name} ({len(df):,} rows)\n"
        f"Accuracy: {accuracy:.2%}\n\n"
        "Classification Report:\n"
        f"{report}\n"
        f"Confusion matrix saved to: {MATRIX_PATH}\n"
        f"Model saved to: {MODEL_PATH}\n"
    )

    REPORT_PATH.write_text(output, encoding="utf-8")
    joblib.dump({"model": model, "label_encoder": label_encoder}, MODEL_PATH)

    print(output)


if __name__ == "__main__":
    main()
