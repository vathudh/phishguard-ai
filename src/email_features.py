import re
from typing import Iterable
from urllib.parse import urlparse

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


URL_RE = re.compile(r"https?://[^\s)>\"]+|www\.[^\s)>\"]+", re.IGNORECASE)
IP_URL_RE = re.compile(r"https?://(?:\d{1,3}\.){3}\d{1,3}", re.IGNORECASE)

SUSPICIOUS_WORDS = {
    "urgent",
    "immediately",
    "verify",
    "password",
    "suspended",
    "locked",
    "confirm",
    "billing",
    "payment",
    "refund",
    "prize",
    "winner",
    "claim",
    "account",
    "security",
    "fraud",
    "credential",
    "reactivate",
    "termination",
    "expires",
    "wire",
    "transfer",
    "routing",
    "deposit",
    "approval",
}

SAFE_CONTEXT_WORDS = {
    "meeting",
    "agenda",
    "minutes",
    "appointment",
    "newsletter",
    "receipt",
    "attached",
    "schedule",
    "reminder",
    "confirmed",
    "review",
}

SHORTENERS = {"bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd"}


class EmailFeatureExtractor(BaseEstimator, TransformerMixin):
    """Convert email text into phishing-focused numeric features."""

    def fit(self, X: Iterable[str], y=None):
        return self

    def transform(self, X: Iterable[str]):
        rows = [self._extract_features(str(text)) for text in X]
        return np.asarray(rows, dtype=float)

    def _extract_features(self, text: str):
        lowered = text.lower()
        urls = URL_RE.findall(text)
        domains = [self._domain(url) for url in urls]
        words = re.findall(r"[a-zA-Z]+", lowered)

        suspicious_hits = sum(1 for word in words if word in SUSPICIOUS_WORDS)
        safe_hits = sum(1 for word in words if word in SAFE_CONTEXT_WORDS)
        exclamation_count = text.count("!")
        digit_count = sum(ch.isdigit() for ch in text)
        uppercase_words = sum(1 for word in re.findall(r"\b[A-Z]{2,}\b", text) if len(word) > 1)
        shortener_count = sum(1 for domain in domains if domain in SHORTENERS)
        suspicious_tld_count = sum(
            1 for domain in domains if domain.endswith((".info", ".biz", ".cc", ".co"))
        )

        return [
            len(text),
            len(words),
            len(urls),
            len(set(domains)),
            suspicious_hits,
            safe_hits,
            exclamation_count,
            digit_count,
            uppercase_words,
            shortener_count,
            suspicious_tld_count,
            int(bool(IP_URL_RE.search(text))),
            int("password" in lowered),
            int("bank" in lowered or "billing" in lowered or "payment" in lowered),
            int("click" in lowered or "login" in lowered or "sign in" in lowered),
        ]

    @staticmethod
    def _domain(url: str):
        if url.lower().startswith("www."):
            url = "http://" + url
        parsed = urlparse(url)
        return parsed.netloc.lower().removeprefix("www.")
