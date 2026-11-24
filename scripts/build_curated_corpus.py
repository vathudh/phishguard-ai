"""Build PhishGuard's documented training corpus from local public-source files.

Inputs:
  data/raw/enron_public.csv   - label 0 is used as legitimate mail
  data/raw/nazario_public.csv - label 1 is used as phishing mail

The Enron source's label-1 messages are intentionally excluded: generic spam is
not automatically phishing and would make the binary labels less trustworthy.
"""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUTPUT = ROOT / "data" / "training_emails.csv"
MAX_PER_CLASS = 1_500


def clean_text(series):
    return (
        series.fillna("")
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )


def main():
    enron = pd.read_csv(RAW / "enron_public.csv", low_memory=False)
    nazario = pd.read_csv(RAW / "nazario_public.csv", low_memory=False)

    safe = enron.loc[enron["label"] == 0, ["subject", "body"]].copy()
    safe["email_text"] = clean_text(safe["subject"]) + " " + clean_text(safe["body"])
    safe = safe.assign(label="safe", source="Enron legitimate subset")

    phishing = nazario.loc[nazario["label"] == 1, ["subject", "body"]].copy()
    phishing["email_text"] = clean_text(phishing["subject"]) + " " + clean_text(phishing["body"])
    phishing = phishing.assign(label="phishing", source="Nazario phishing corpus")

    dataset = pd.concat(
        [safe[["label", "email_text", "source"]], phishing[["label", "email_text", "source"]]],
        ignore_index=True,
    )
    dataset = dataset[dataset["email_text"].str.len() >= 40]
    dataset = dataset.drop_duplicates(subset=["email_text"])

    balanced = (
        dataset.groupby("label", group_keys=False)
        .apply(lambda group: group.sample(n=min(len(group), MAX_PER_CLASS), random_state=42))
        .sample(frac=1, random_state=42)
        .reset_index(drop=True)
    )
    if balanced["label"].nunique() != 2:
        raise ValueError("Expected both phishing and safe classes.")

    OUTPUT.write_text(balanced.to_csv(index=False), encoding="utf-8")
    print(f"Saved {len(balanced):,} emails to {OUTPUT}")
    print(balanced.groupby(["label", "source"]).size().to_string())


if __name__ == "__main__":
    main()
