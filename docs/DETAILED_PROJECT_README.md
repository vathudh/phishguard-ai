# PhishGuard AI - Detailed Project Guide

## 1. Project Identity

**Project name:** PhishGuard AI - Explainable Phishing Email Detection and Threat Analysis Platform  
**Domain:** Cybersecurity, Machine Learning, Full-Stack Web Development  
**Repository:** https://github.com/vathudh/phishguard-ai  
**Primary stack:** Python, Flask, Scikit-learn, SQLite, HTML, CSS, JavaScript, Docker  
**Current deployment state:** Fully runnable locally; Docker and Render deployment assets are included. Vercel deployment needs a serverless storage adaptation as described in Section 17.

PhishGuard AI is a local-first web application that helps a user inspect suspicious email content. It does not merely return a label. It combines a trained machine-learning classifier with transparent cybersecurity checks and explains the evidence behind its result.

The intended user journey is simple:

1. Paste an email or upload an `.eml` file.
2. Run the scan.
3. Receive a verdict, risk score, model confidence, phishing probability, technical indicators, and URL analysis.
4. Record whether the result was correct.
5. Review locally stored scan history or export it as JSON.

## 2. Problem Statement

Phishing emails use fraudulent links, impersonated senders, urgent language, malicious attachments, and requests for credentials to manipulate users. Many basic email classifiers provide only a binary result, leaving the user unable to understand why an email is risky.

PhishGuard AI addresses two connected problems:

- **Detection:** identify email content likely to be phishing.
- **Explainability:** display the observable signals that contributed to the decision, such as an IP-address URL, a shortened link, urgency language, a password request, or a suspected brand-impersonation pattern.

The project is designed for education, research demonstrations, and first-pass triage. It is not a replacement for an enterprise email-security gateway or a human security analyst.

## 3. Objectives

1. Build a reusable phishing-email classifier using Scikit-learn.
2. Train on a documented balanced corpus of phishing and legitimate email content.
3. Extract text and security-focused URL features.
4. Provide a browser interface instead of only a command-line model.
5. Make predictions understandable to non-expert users.
6. Store local scan history and analyst feedback without requiring a cloud account.
7. Provide automated tests, Docker packaging, GitHub CI, and deployment guidance.

## 4. Implemented Features

### Email intake

- Paste an email subject, sender, and body directly into the dashboard.
- Upload standard `.eml` files up to 2 MB.
- Parse readable plain-text and HTML email parts.
- Ignore attachments rather than opening or executing them.
- Reject empty or extremely short content before model inference.

### Explainable threat analysis

- Classify the message as **Phishing**, **Suspicious**, or **Likely Safe**.
- Show a normalized risk score from 0 to 100.
- Show model confidence and phishing/safe probabilities.
- Detect social-engineering vocabulary, urgent pressure, sensitive-data requests, excessive capitalization, and possible sender impersonation.
- Extract URLs and identify structural risks such as IP-address destinations, URL shorteners, high-risk top-level domains, complex domains, and simple obfuscation patterns.
- Show an action-oriented recommendation for each verdict.

### Local evidence and feedback

- Store scan metadata in SQLite.
- Store a maximum 500-character preview, not the complete raw email body.
- Record user feedback as `phishing` or `safe`.
- Display recent scan history.
- Export scan history as JSON.

### Engineering and delivery

- Flask REST API with input validation and error responses.
- Security headers for framing, MIME sniffing, referrer policy, and a restrictive content-security policy.
- Automated API tests using pytest.
- Dockerfile, `.dockerignore`, start script, and Render Blueprint configuration.
- GitHub Actions workflow that runs tests on push and pull request.
- Windows startup script for simple local execution.

## 5. High-Level Architecture

```text
                    +-----------------------------+
                    |  Browser Dashboard           |
                    |  Paste text / Upload .eml    |
                    +--------------+--------------+
                                   |
                                   v
                    +-----------------------------+
                    | Flask Application and API    |
                    | /api/scan, /api/history      |
                    +------+------------------+----+
                           |                  |
                           v                  v
             +-----------------------+  +----------------------+
             | ML and Rule Engine    |  | SQLite Repository    |
             | TF-IDF + SVM          |  | Local history        |
             | URL and text signals  |  | Feedback and export  |
             +-----------+-----------+  +----------------------+
                         |
                         v
             +-----------------------+
             | Verdict + Risk Score  |
             | Explanation + URLs    |
             +-----------------------+
```

### 5.1 Component Responsibilities

| Layer | Components | Responsibility |
|---|---|---|
| Presentation | `templates/index.html`, `static/styles.css`, `static/app.js` | Provides the scan form, risk display, explanation panels, local history, feedback, and export controls. |
| Web/API | `app.py` | Defines Flask routes, validates requests, handles `.eml` uploads, applies response security headers, and coordinates storage. |
| Parsing | `extract_eml_text()` | Extracts readable plain-text or HTML message content while skipping attachments. |
| ML feature layer | `email_features.py` | Produces TF-IDF text features and numerical phishing signals such as URL count, urgent vocabulary, IP URLs, and suspicious TLDs. |
| Classification layer | Scikit-learn pipeline | Uses a calibrated LinearSVC to estimate phishing and safe probabilities. |
| Explainability layer | `security_analyzer.py` | Converts model output and rule findings into a human-readable verdict, risk score, URL intelligence, and recommendation. |
| Persistence layer | `database.py`, SQLite | Stores a limited email preview, verdict, score, indicators, timestamps, and user feedback locally. |
| Delivery layer | Docker, Waitress, GitHub Actions | Supports reproducible local execution, container deployment, and automated test execution. |

### 5.2 Detailed Request Flow

```text
1. User submits pasted content or an .eml file.
2. Flask validates file size, content length, and extension.
3. The parser extracts subject, sender, and readable email body.
4. The ML pipeline converts content into TF-IDF and numeric security features.
5. The calibrated classifier estimates phishing and safe probabilities.
6. The rule engine inspects urgency, credentials, sender mismatch, and URLs.
7. The hybrid score blends ML phishing probability with rule-based risk.
8. SQLite saves a privacy-limited scan record and optional feedback.
9. The browser receives verdict, score, evidence, URLs, and recommendation.
```

### 5.3 Deployment Boundaries

```text
Local / Docker / Render
  Browser --> Flask + ML model --> SQLite or mounted persistent data volume

Vercel serverless adaptation
  Browser --> Flask function + ML model --> external managed database
```

The local version is fully implemented. A Vercel production deployment must replace persistent SQLite storage with a managed database because serverless filesystem storage is not durable.

## 6. Project Structure

```text
phishing_email_detection_model/
|
|-- app.py                         Flask application factory and API routes
|-- requirements.txt               Runtime and test dependencies
|-- run_local.ps1                  Windows setup-and-run helper
|-- Dockerfile                     Container image definition
|-- start.sh                       Production Waitress startup script
|-- render.yaml                    Render Blueprint configuration
|-- Procfile                       Generic process declaration
|
|-- data/
|   |-- sample_emails.csv          Small safe demo dataset committed to Git
|   |-- README.md                  Dataset provenance and preparation notes
|   |-- raw/                       Downloaded public corpus files, ignored by Git
|   |-- training_emails.csv        Generated curated corpus, ignored by Git
|   `-- phishguard.db              Local runtime database, ignored by Git
|
|-- models/
|   |-- phishing_email_model.joblib  Versioned trained model artifact
|   |-- metrics_report.txt           Latest evaluation report
|   `-- confusion_matrix.png         Latest confusion matrix image
|
|-- src/
|   |-- email_features.py          Custom numerical feature transformer
|   |-- security_analyzer.py       ML prediction and threat explanation engine
|   |-- database.py                SQLite persistence layer
|   |-- train_model.py             Training and evaluation workflow
|   `-- predict_email.py           Command-line prediction utility
|
|-- scripts/
|   |-- build_curated_corpus.py    Builds the 3,000-email corpus locally
|   `-- prepare_dataset.py         Normalizes a future external CSV
|
|-- templates/index.html           Dashboard markup
|-- static/styles.css              Responsive dashboard style sheet
|-- static/app.js                  Dashboard API interactions
|-- tests/test_app.py              Automated API tests
|-- docs/                          Report, hosting, and project documentation
`-- .github/workflows/ci.yml       GitHub Actions test workflow
```

## 7. Machine Learning Design

### 7.1 Text representation

The model uses `TfidfVectorizer` to convert the email text into numerical features. The current configuration:

- Lowercases input text.
- Removes English stop words.
- Includes unigrams and bigrams (`ngram_range=(1, 2)`).
- Limits text vocabulary to 1,500 features.

This lets the classifier learn meaningful terms and short phrases such as `verify account`, `payment failed`, or `meeting agenda`.

### 7.2 Handcrafted security features

The custom `EmailFeatureExtractor` adds 15 numeric phishing-oriented signals:

1. Total text length.
2. Word count.
3. URL count.
4. Unique URL-domain count.
5. Count of suspicious vocabulary matches.
6. Count of safe-context vocabulary matches.
7. Exclamation-mark count.
8. Digit count.
9. Capitalized-word count.
10. Shortened-link count.
11. Suspicious-TLD count.
12. IP-address URL flag.
13. Password-reference flag.
14. Banking/billing/payment-reference flag.
15. Click/login/sign-in request flag.

### 7.3 Classifier

The final estimator is a `LinearSVC` wrapped in `CalibratedClassifierCV`. Calibration provides usable class probabilities, which are required for a user-facing phishing likelihood and confidence display.

The complete Scikit-learn pipeline is:

```text
Email text
   |
   +--> TF-IDF unigram/bigram features
   |
   +--> Custom URL and linguistic features
   |
   +--> ColumnTransformer combines both feature groups
   |
   +--> Calibrated Linear Support Vector Classifier
   |
   `--> Safe / Phishing probability
```

### 7.4 Product risk score

The dashboard risk score is intentionally not identical to the ML probability. It blends two evidence sources:

```text
risk_score = min(100, 0.65 x phishing_probability + 0.35 x rule_score)
```

Where `rule_score` is based on transparent security evidence. The current verdict thresholds are:

| Risk score | Verdict | Meaning |
|---:|---|---|
| 70 to 100 | Phishing | Strongly suspicious; do not click or share data. |
| 40 to 69 | Suspicious | Verify the sender using an official channel. |
| 0 to 39 | Likely Safe | No major signals found; remain cautious. |

This hybrid decision is useful for an academic project because the system can explain its result rather than hiding all reasoning inside a model.

## 8. Dataset Pipeline and Provenance

### 8.1 Current curated corpus

The model is currently trained on `3,000` curated messages:

| Class | Count | Source subset |
|---|---:|---|
| Phishing | 1,500 | Nazario phishing corpus, source label `1` |
| Safe | 1,500 | Enron dataset, source label `0` |
| Total | 3,000 | Balanced research baseline |

The `scripts/build_curated_corpus.py` process:

1. Reads local copies of the public Enron and Nazario CSV files.
2. Uses Enron's label `0` as the legitimate class.
3. Uses Nazario's label `1` as the phishing class.
4. Excludes Enron label `1` because generic spam should not automatically be called phishing.
5. Combines subject and body fields.
6. Removes extremely short records.
7. Removes duplicate text.
8. Samples up to 1,500 examples per class using a fixed random seed.
9. Shuffles and writes `data/training_emails.csv`.

The generated corpus contains zero exact duplicate messages and has a median email length of 758 characters.

### 8.2 Why raw data is not in GitHub

The downloaded raw data can contain large email content and has its own source/license conditions. It is excluded by `.gitignore` to keep the public repository small and responsible. The training builder and source documentation are versioned so the process remains reproducible.

### 8.3 Important evaluation caution

The curated corpus is a credible academic baseline, not proof of production-grade performance. The phishing and safe classes come from different source corpora, so dataset-source characteristics can influence results. A stronger future evaluation should add more sources, temporal splitting, and cross-corpus testing.

## 9. Current Evaluation Results

The training script uses a stratified 75/25 train/test split with `random_state=42`.

| Metric | Phishing | Safe | Overall |
|---|---:|---:|---:|
| Precision | 0.93 | 0.89 | - |
| Recall | 0.89 | 0.93 | - |
| F1-score | 0.91 | 0.91 | - |
| Support | 375 | 375 | 750 |
| Accuracy | - | - | **90.93%** |

The model is therefore evaluated on 750 held-out messages. This number is appropriate for the report and demonstration. Do not replace it with a claim of 100% real-world accuracy.

The latest generated evidence is stored in:

- `models/metrics_report.txt`
- `models/confusion_matrix.png`
- `models/phishing_email_model.joblib`

## 10. Threat Explanation Rules

The application checks for the following human-readable indicators in addition to ML probability.

| Indicator | Example evidence | Why it matters |
|---|---|---|
| Social engineering | `urgent`, `verify`, `password`, `refund` | Common manipulation vocabulary. |
| Action request | `click`, `login`, `sign in`, `download` | Encourages the victim to act quickly. |
| Urgency pressure | `immediately`, `final notice`, `within 24 hours` | Reduces time for careful inspection. |
| Sensitive information request | Password, OTP, card, seed phrase | Potential credential or financial theft. |
| Sender impersonation | Brand claim sent from a consumer mailbox | Possible mismatch between sender and claimed organization. |
| IP-address URL | `http://198.51.100.12/login` | Avoids a recognizable domain identity. |
| URL shortener | `bit.ly`, `tinyurl.com` | Can conceal the final destination. |
| Risky domain pattern | Unusual TLD or complex hyphenated host | Structural signal requiring further verification. |

These rules are intentionally explainable. They should be treated as signals, not absolute proof of malicious intent.

## 11. Web Application and API

### Dashboard capabilities

The dashboard provides:

- Subject, sender, and email-body fields.
- A preloaded phishing demo for presentation use.
- `.eml` upload input.
- Circular risk visualization.
- Verdict and recommendation panel.
- Machine-learning probability and confidence display.
- Explanation list and URL-intelligence cards.
- Feedback buttons.
- Recent local activity list.
- JSON history export.

### API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Loads the dashboard. |
| `POST` | `/api/scan` | Scans manually entered subject, sender, and body data. |
| `POST` | `/api/upload-eml` | Parses and scans an uploaded `.eml` file. |
| `GET` | `/api/history` | Returns the latest 30 locally stored scans. |
| `POST` | `/api/scans/<id>/feedback` | Saves `safe` or `phishing` analyst feedback. |
| `GET` | `/api/export` | Downloads history as JSON. |

### Request example

```json
{
  "subject": "Urgent: account verification required",
  "sender": "Security Alert <notice@gmail.com>",
  "email_text": "Verify your password immediately at http://198.51.100.12/login."
}
```

## 12. Privacy and Security Measures

The project uses a local-first design for the default run:

- Raw email content stays in the running process during analysis.
- The database saves only a 500-character preview plus result metadata.
- `.eml` attachments are skipped and never executed.
- File uploads are limited to 2 MB.
- Manual input is limited to 100,000 characters.
- The interface renders result data with HTML escaping to avoid script injection from hostile email content.
- Responses include `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, and Content-Security-Policy headers.

### What PhishGuard does not do yet

- It does not verify SPF, DKIM, or DMARC headers.
- It does not scan attachments for malware.
- It does not check live domain reputation feeds.
- It does not perform Unicode homoglyph detection.
- It does not authenticate end users or encrypt the local SQLite file.
- It must not be used as the sole security control for a company inbox.

## 13. Local Setup and Run Instructions

### Prerequisites

- Windows 10/11, macOS, or Linux.
- Python 3.12 recommended.
- Internet access for first-time dependency installation.

### Windows quick start

```powershell
cd phishing_email_detection_model
.\run_local.ps1
```

Then open `http://127.0.0.1:5000`.

### Manual setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### Retrain the model

```powershell
python -m src.train_model
```

When `data/training_emails.csv` is present, the script uses it. Otherwise, it falls back to the committed 40-message demonstration CSV.

### Rebuild the local curated dataset

Place the source CSV files in `data/raw/`, then run:

```powershell
python scripts/build_curated_corpus.py
python -m src.train_model
```

## 14. Tests and Quality Checks

Run the automated tests with:

```powershell
python -m pytest tests -q
```

The current suite has four API-level tests:

1. Dashboard response loads.
2. Very short email input is rejected.
3. A phishing-like message returns explainable indicators and URL findings.
4. Scan history and feedback persistence work.

GitHub Actions runs these tests on each push and pull request.

## 15. Docker and Render Deployment

### Docker

```powershell
docker build -t phishguard-ai .
docker run --rm -p 5000:5000 -v "${PWD}/runtime-data:/var/data" -e PHISHGUARD_DATA_DIR=/var/data phishguard-ai
```

Open `http://127.0.0.1:5000`.

### Render

The repository includes `render.yaml` for a Python web-service deployment. It uses Waitress, a production WSGI server, rather than Flask's development server. A mounted disk at `/var/data` is configured for SQLite history when the selected Render plan supports persistent disks.

Read `docs/HOSTING.md` before deployment.

## 16. GitHub Repository Hygiene

The public repository intentionally includes:

- Application source code.
- Unit/API tests.
- Documentation.
- The compact trained model artifact.
- Evaluation report and confusion matrix.
- Demo data.
- Deployment files and CI workflow.

It intentionally excludes:

- `data/raw/` public corpus downloads.
- `data/training_emails.csv` generated training data.
- `data/phishguard.db` local runtime data.
- `data/exports/` user-generated exports.
- `.venv/`, cache directories, and Python bytecode.

This protects local information and avoids publishing large raw email corpora unnecessarily.

## 17. Vercel Deployment Note

Vercel is a good platform for the dashboard and Flask API, but the current SQLite-history design cannot persist reliably in Vercel's serverless filesystem. A Vercel adaptation should use one of these approaches:

1. **Demo mode:** use temporary history only. The classifier and dashboard work, but scan history can disappear after a serverless restart.
2. **Production project mode:** use a persistent managed database such as Neon PostgreSQL or Supabase PostgreSQL for scan history and feedback.

Before a Vercel deployment, make these project changes:

- Export a module-level Flask `app` object compatible with Vercel's Python runtime.
- Move database configuration to environment variables.
- Replace SQLite with a managed database or explicitly disable history in demo mode.
- Configure the Vercel project to include `models/phishing_email_model.joblib` in the Python function bundle.
- Keep the deployed model and dependencies under Vercel function size limits.

Do not claim persistent scan history on Vercel until a persistent external database has actually been connected and tested.

## 18. Suggested Internship Demonstration Flow

1. Start with the phishing problem: fraudulent email remains a common entry point for credential theft.
2. Open the PhishGuard dashboard.
3. Load the built-in phishing demo.
4. Run the scan and explain the risk score.
5. Point out the IP-address URL, urgency wording, password request, and sender mismatch.
6. Mark feedback and show local history.
7. Export history as JSON.
8. Show the confusion matrix and explain the 3,000-message dataset and 90.93% hold-out accuracy.
9. Open the GitHub repository and show source code, tests, CI, and documentation.
10. Close with limitations and next steps, demonstrating honest engineering judgment.

## 19. Viva Questions and Honest Answers

### Why did you use a hybrid model plus rules?

The ML model captures patterns across language and features, while rules make the final result understandable. A cybersecurity user needs to know what to inspect, not only a label.

### Why is the score not identical to model confidence?

The score also includes visible threat indicators. A message with a high-risk IP URL and a credential request should communicate that evidence clearly even when the language alone is uncertain.

### Why did you use LinearSVC instead of a deep-learning model?

For a 3,000-message baseline corpus, TF-IDF plus a linear classifier is computationally efficient, explainable, fast on a normal laptop, and appropriate for a reproducible academic baseline. A transformer is a future comparative experiment, not a claim already made by this project.

### How did you avoid data leakage?

The pipeline uses a stratified train/test split with a fixed seed, and duplicate exact message text is removed during corpus construction. The report must also acknowledge that separate corpus sources can still create source-specific bias.

### What are the major limitations?

Older corpus sources, limited data diversity, no live reputation feed, no authentication-header checks, no attachment scanning, and SQLite-only persistence are the major current limitations.

### How would you make it production-ready?

Use a larger multi-source and time-split corpus, add SPF/DKIM/DMARC parsing, domain reputation checks, attachment sandbox integration, authentication, encrypted managed storage, security monitoring, rate limiting, and human analyst review.

## 20. Work Completed Checklist

- [x] Created a Flask web interface.
- [x] Added Scikit-learn text and security-feature pipeline.
- [x] Added explainable hybrid risk scoring.
- [x] Added manual entry and `.eml` upload workflows.
- [x] Added URL intelligence and human-readable indicators.
- [x] Added SQLite local history, feedback, and export.
- [x] Built a curated 3,000-message research corpus locally.
- [x] Trained and saved a model with a 90.93% hold-out result.
- [x] Generated a confusion matrix and metrics report.
- [x] Added API tests and GitHub Actions CI.
- [x] Added Docker, Render, and local-run configurations.
- [x] Published the safe project files to GitHub.
- [ ] Adapt persistent storage before a Vercel production deployment.
- [ ] Capture final screenshots and prepare the formal internship report.
- [ ] Add a Vercel URL after a successful deployment.

## 21. Credits and Source Acknowledgement

- Scikit-learn for the ML pipeline.
- Flask for the web application framework.
- The public Enron and Nazario source subsets used by the local corpus builder.
- The public Phishing-Email-Dataset repository used to obtain the source CSV files.
- The PhishGuard AI project author for system design, integration, model development, testing, and documentation.

---

For quick setup, use the root `README.md`. For report writing, use `docs/FINAL_YEAR_PROJECT_REPORT.md`. For hosting instructions, use `docs/HOSTING.md`.
