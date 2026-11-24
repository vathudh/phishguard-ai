# PhishGuard AI

PhishGuard AI is an explainable phishing-email analysis platform. It combines a Scikit-learn classifier with transparent URL, linguistic, credential-theft, and sender-impersonation checks. The dashboard works locally and stores scan history in SQLite.

For the complete technical architecture, data pipeline, evaluation, API reference, security design, deployment details, viva preparation, and work-completed record, read [docs/DETAILED_PROJECT_README.md](docs/DETAILED_PROJECT_README.md).

## Brief Project Description

PhishGuard AI is a cybersecurity web application that helps users inspect suspicious emails before interacting with them. A user can paste an email or upload an `.eml` file. The system extracts text and URL features, applies a trained Scikit-learn classifier, checks transparent phishing indicators, and returns a phishing/suspicious/safe verdict with a risk score and explanation. It also keeps local scan history and feedback for demonstration and review.

## Architecture at a Glance

```text
User browser
    |
    | Paste email / Upload .eml
    v
Flask dashboard and REST API
    |
    +--> Email parsing and validation
    |
    +--> ML pipeline: TF-IDF + security features + calibrated LinearSVC
    |
    +--> Explainability engine: URL, urgency, credential, sender checks
    |
    +--> SQLite: local scan history and analyst feedback
    |
    v
Verdict, 0-100 risk score, evidence, recommendation, export
```

## Features

- Paste an email or upload a `.eml` file.
- Receive phishing/suspicious/safe verdict, risk score, model confidence, and explanation.
- Analyze URLs for IP-address destinations, shorteners, risky TLDs, and obfuscation.
- Keep scan history and analyst feedback locally in SQLite.
- Export history as JSON.
- Run REST API tests and package with Docker.

## Project Structure

```text
app.py                          Flask application and REST API
templates/                      Web dashboard
static/                         Dashboard styling and behaviour
src/security_analyzer.py        Explainable ML + threat-analysis engine
src/database.py                 Local SQLite persistence
src/train_model.py              Training and evaluation script
scripts/prepare_dataset.py      Public-dataset normalization utility
scripts/build_curated_corpus.py Reproducible Enron + Nazario corpus builder
tests/                          Automated API tests
docs/                           Submission-report material
models/                         Generated model and evaluation files
```

## Setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If `py -3.12` is unavailable, use your installed Python 3.10+ interpreter.

## Run the Web Application

```powershell
python app.py
```

Open `http://127.0.0.1:5000` in a browser.

For Windows, you can alternatively run:

```powershell
.\run_local.ps1
```

## Run Automated Tests

```powershell
python -m pytest tests -q
```

## Train and Evaluate

```bash
python -m src.train_model
```

The script prints the model accuracy and classification report. It also writes:

- `models/phishing_email_model.joblib`
- `models/confusion_matrix.png`
- `models/metrics_report.txt`

## Train the Model

```powershell
python src/train_model.py
```

This refreshes `models/phishing_email_model.joblib`, `models/metrics_report.txt`, and `models/confusion_matrix.png`.

When `data/training_emails.csv` exists, training automatically uses the curated 3,000-message corpus rather than the 40-message starter sample.

## Command-line Prediction

```bash
python src/predict_email.py "URGENT: your account is locked. Verify your password at http://example-login.com"
```

Example output:

```text
Prediction: Phishing
Probabilities:
  phishing: 93.20%
  safe: 6.80%
```

## Docker

```powershell
docker build -t phishguard-ai .
docker run -p 5000:5000 phishguard-ai
```

## GitHub and Hosting

The repository is ready for GitHub and Render deployment. See [docs/HOSTING.md](docs/HOSTING.md) for the safe upload checklist, Render Blueprint steps, and Docker deployment.

The trained model is versioned so the hosted app can start immediately. Raw public corpus files, generated training data, scan history, and exports are intentionally excluded from GitHub.

## Using Your Own Dataset

Replace `data/sample_emails.csv` with a larger dataset containing these columns:

- `label`: `phishing` or `safe`
- `email_text`: the raw email subject/body text

For best real-world performance, use a larger, representative dataset and keep a separate test set that was not used during training. Do not claim the sample-dataset score as real-world accuracy.

See [data/README.md](data/README.md) for the dataset preparation process and provenance requirements.
