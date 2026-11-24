# PhishGuard AI: Explainable Phishing Email Detection and Threat Analysis Platform

## Abstract

PhishGuard AI is a local-first cybersecurity application that classifies suspicious emails and explains the signals behind its decision. It combines a calibrated machine-learning text classifier with transparent rule-based analysis of URLs, social-engineering language, credential requests, urgency, and probable sender impersonation. Users can paste email text or upload `.eml` files, inspect a risk score and technical indicators, then retain feedback and scan history locally in SQLite.

## Problem Statement

Phishing emails remain one of the most common delivery mechanisms for credential theft, financial fraud, and malware. Traditional spam warnings often do not explain the reason for a decision. This project addresses that gap by combining predictive classification with understandable threat evidence.

## Objectives

1. Classify email content as phishing, suspicious, or likely safe.
2. Analyze URLs, linguistic pressure, credential requests, and sender anomalies.
3. Display a transparent risk score and actionable explanation.
4. Store scan history and human feedback locally for privacy.
5. Provide a deployable web interface with API endpoints and tests.

## System Architecture

```text
Browser dashboard / .eml upload
        |
Flask REST API
        |
ML classifier + security rules engine
        |                         |
Risk score + explanations     SQLite local history
        |
Dashboard result and JSON export
```

## Machine Learning Method

The classification pipeline uses TF-IDF unigram/bigram text representation and manually engineered features: URL count, IP-address URLs, shortener detection, suspicious TLDs, urgency/credential vocabulary, capitalization, and action-request terms. A calibrated Linear Support Vector Classifier produces class probabilities. The product-level risk score blends phishing probability with transparent rule-based indicators; this improves interpretability and avoids presenting the model as infallible.

## Evaluation

The included starter dataset is intentionally small and demonstrative. The training script performs a stratified 75/25 train/test split and saves a classification report and confusion matrix. The current held-out demonstration result is 100% on 10 test messages; this must not be reported as real-world accuracy. For final submission, replace the starter data with an approved, larger public corpus and report results on a blind hold-out test set and k-fold cross-validation.

Recommended public data sources to document in the final report:

- Nazario phishing corpus
- Enron email corpus for legitimate email samples
- PhishTank URL intelligence feeds, subject to their terms of use

## Security and Privacy Design

- Default operation is local-first: raw emails are not sent to an external SaaS service.
- SQLite stores a 500-character preview rather than full raw content.
- `.eml` uploads are size-limited to 2 MB and attachments are ignored.
- Security headers protect the browser interface from framing and MIME sniffing.
- The UI escapes untrusted email-derived content before rendering it.

## Software Stack

- Python, Flask, SQLite
- Scikit-learn, pandas, NumPy
- HTML, CSS, JavaScript
- Docker for reproducible execution
- pytest for automated API tests

## Limitations and Future Work

The supplied model should be treated as an educational baseline. It does not inspect live domain reputation, email authentication headers (SPF/DKIM/DMARC), attachment malware, or adversarially crafted Unicode domains. Future work can add a larger ethically sourced corpus, separate model validation, URL reputation APIs, user authentication, encrypted storage, and an analyst/admin dashboard.

## Demo Script

1. Open the dashboard and load the supplied phishing demo.
2. Run the security scan.
3. Explain the phishing probability, IP-address URL, urgency language, and credential request.
4. Mark the result as correct/incorrect and show that feedback enters local history.
5. Export history as JSON, showing privacy-preserving local data handling.
