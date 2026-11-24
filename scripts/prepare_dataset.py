"""Normalize a public email dataset into PhishGuard's training schema.

Usage:
python scripts/prepare_dataset.py raw_emails.csv data/training_emails.csv \
  --text-column body --label-column category
"""

import argparse
from pathlib import Path

import pandas as pd


LABEL_MAP = {
    "phishing": "phishing",
    "phish": "phishing",
    "spam": "phishing",
    "malicious": "phishing",
    "safe": "safe",
    "ham": "safe",
    "legitimate": "safe",
    "benign": "safe",
}


def main():
    parser = argparse.ArgumentParser(description="Prepare a labeled email corpus for PhishGuard training.")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--text-column", default="email_text")
    parser.add_argument("--label-column", default="label")
    parser.add_argument("--max-per-class", type=int, default=0)
    args = parser.parse_args()

    raw = pd.read_csv(args.input_csv)
    required = {args.text_column, args.label_column}
    missing = required - set(raw.columns)
    if missing:
        raise ValueError(f"CSV is missing expected columns: {', '.join(sorted(missing))}")

    dataset = raw[[args.text_column, args.label_column]].rename(
        columns={args.text_column: "email_text", args.label_column: "label"}
    )
    dataset["label"] = dataset["label"].astype(str).str.strip().str.lower().map(LABEL_MAP)
    dataset["email_text"] = dataset["email_text"].fillna("").astype(str).str.strip()
    dataset = dataset.dropna(subset=["label"])
    dataset = dataset[dataset["email_text"].str.len() >= 20]
    dataset = dataset.drop_duplicates(subset=["email_text"])

    if args.max_per_class:
        dataset = (
            dataset.groupby("label", group_keys=False)
            .apply(lambda group: group.sample(min(len(group), args.max_per_class), random_state=42))
            .reset_index(drop=True)
        )

    if dataset["label"].nunique() != 2:
        raise ValueError("Prepared data must contain both phishing and safe examples.")

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    dataset.sample(frac=1, random_state=42).to_csv(args.output_csv, index=False)
    print(f"Saved {len(dataset)} rows to {args.output_csv}")
    print(dataset["label"].value_counts().to_string())


if __name__ == "__main__":
    main()
