import email
import ipaddress
import re
from email import policy
from email.parser import BytesParser
from pathlib import Path
from urllib.parse import urlparse

import joblib
import pandas as pd

from src.email_features import SHORTENERS, SUSPICIOUS_WORDS, URL_RE

BRAND_WORDS = {"paypal", "microsoft", "google", "apple", "amazon", "netflix", "dhl", "fedex"}
HIGH_RISK_TLDS = {".zip", ".mov", ".top", ".xyz", ".click", ".work", ".gq", ".tk"}
ACTION_WORDS = {"click", "login", "sign in", "download", "open attachment", "update", "verify"}


class EmailSecurityAnalyzer:
    """Combines the trained ML model with transparent security checks."""

    def __init__(self, model_path):
        self.bundle = joblib.load(Path(model_path))
        self.model = self.bundle["model"]
        self.label_encoder = self.bundle["label_encoder"]

    def analyze(self, email_text, subject="", sender=""):
        combined_text = " ".join(part for part in [subject, sender, email_text] if part).strip()
        probabilities = self.model.predict_proba(pd.DataFrame({"email_text": [combined_text]}))[0]
        probability_by_label = {
            self.label_encoder.inverse_transform([index])[0]: float(value)
            for index, value in enumerate(probabilities)
        }
        ml_probability = probability_by_label.get("phishing", 0.0)
        indicators = self._extract_indicators(combined_text, sender)
        heuristic_score = min(100, sum(item["weight"] for item in indicators))
        risk_score = round(min(100, (ml_probability * 65) + (heuristic_score * 0.35)))

        if risk_score >= 70:
            verdict, severity, action = "Phishing", "high", "Do not click links or share information. Report this email to your security team."
        elif risk_score >= 40:
            verdict, severity, action = "Suspicious", "medium", "Verify the sender using an official channel before taking any action."
        else:
            verdict, severity, action = "Likely Safe", "low", "No strong phishing signals were found. Stay alert for unexpected requests."

        return {
            "verdict": verdict,
            "severity": severity,
            "risk_score": risk_score,
            "model_confidence": round(max(probability_by_label.values()) * 100, 1),
            "phishing_probability": round(ml_probability * 100, 1),
            "safe_probability": round(probability_by_label.get("safe", 0.0) * 100, 1),
            "indicators": indicators,
            "urls": self._analyze_urls(combined_text),
            "recommendation": action,
            "analysis_version": "PhishGuard ML + Rules v1.0",
        }

    def _extract_indicators(self, text, sender):
        lowered = text.lower()
        findings = []

        keyword_hits = sorted({word for word in SUSPICIOUS_WORDS if re.search(rf"\b{re.escape(word)}\b", lowered)})
        if keyword_hits:
            findings.append({"title": "Social-engineering language", "detail": f"Found: {', '.join(keyword_hits[:6])}", "weight": min(28, 6 + len(keyword_hits) * 3), "level": "high"})
        if any(phrase in lowered for phrase in ACTION_WORDS):
            findings.append({"title": "Action request", "detail": "The email pressures the recipient to click, sign in, update, or download.", "weight": 12, "level": "medium"})
        if re.search(r"\b(urgent|immediately|within \d+ hours?|final notice|act now)\b", lowered):
            findings.append({"title": "Urgency pressure", "detail": "Urgent wording is commonly used to bypass careful review.", "weight": 12, "level": "medium"})
        if re.search(r"\b(password|one[- ]time code|otp|credential|bank details|card number|seed phrase)\b", lowered):
            findings.append({"title": "Sensitive information request", "detail": "The message references credentials or financial information.", "weight": 20, "level": "high"})
        if text.count("!") >= 2 or len(re.findall(r"\b[A-Z]{3,}\b", text)) >= 3:
            findings.append({"title": "Unusual emphasis", "detail": "Excessive exclamation marks or capitalized words were detected.", "weight": 6, "level": "low"})
        if sender and re.search(r"@(gmail|yahoo|outlook|hotmail)\.", sender.lower()) and any(brand in lowered for brand in BRAND_WORDS):
            findings.append({"title": "Possible sender impersonation", "detail": "A consumer mailbox claims to represent a known brand.", "weight": 22, "level": "high"})
        if not findings:
            findings.append({"title": "No major rule-based alerts", "detail": "The scan did not find high-confidence social-engineering signals.", "weight": 0, "level": "low"})
        return findings

    def _analyze_urls(self, text):
        analyses = []
        for raw_url in URL_RE.findall(text):
            url = raw_url if raw_url.startswith(("http://", "https://")) else f"http://{raw_url}"
            parsed = urlparse(url)
            domain = parsed.netloc.lower().removeprefix("www.")
            signals = []
            score = 0
            if self._is_ip_domain(domain):
                signals.append("IP address used instead of a domain")
                score += 35
            if domain in SHORTENERS:
                signals.append("URL shortener hides final destination")
                score += 22
            if any(domain.endswith(tld) for tld in HIGH_RISK_TLDS):
                signals.append("High-risk top-level domain")
                score += 18
            if domain.count("-") >= 2 or domain.count(".") >= 3:
                signals.append("Unusually complex domain name")
                score += 10
            if "@" in raw_url or "//" in parsed.path:
                signals.append("Potential URL obfuscation")
                score += 20
            analyses.append({"url": raw_url, "domain": domain, "risk": min(score, 100), "signals": signals or ["No obvious structural URL risk"]})
        return analyses

    @staticmethod
    def _is_ip_domain(domain):
        try:
            ipaddress.ip_address(domain.split(":")[0])
            return True
        except ValueError:
            return False


def extract_eml_text(raw_email):
    try:
        message = BytesParser(policy=policy.default).parsebytes(raw_email)
    except (email.errors.MessageError, UnicodeDecodeError) as error:
        raise ValueError("The uploaded file could not be read as an email.") from error

    subject = str(message.get("subject", ""))
    sender = str(message.get("from", ""))
    body_parts = []
    for part in message.walk():
        if part.get_content_maintype() == "multipart" or part.get_content_disposition() == "attachment":
            continue
        if part.get_content_type() in {"text/plain", "text/html"}:
            try:
                content = part.get_content()
                if part.get_content_type() == "text/html":
                    content = re.sub(r"<[^>]+>", " ", content)
                body_parts.append(content)
            except (LookupError, UnicodeDecodeError):
                continue
    text = "\n".join(body_parts).strip()
    if not text:
        raise ValueError("The email does not contain readable text content.")
    return subject, sender, text
