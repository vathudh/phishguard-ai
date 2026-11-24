# Dataset Notes

`sample_emails.csv` is a small, synthetic demonstration dataset. It is included only so the application can be run immediately. It is not suitable evidence for production accuracy claims.

## Current Curated Corpus

`training_emails.csv` is generated locally by `scripts/build_curated_corpus.py` from two public-source CSV files stored in `data/raw/`:

- **Enron.csv:** only original label `0` is used as legitimate mail.
- **Nazario.csv:** original label `1` is used as phishing mail.

The builder deduplicates messages, removes extremely short records, and randomly samples an equal maximum of 1,500 messages per class. It deliberately excludes Enron's label-1 spam subset because spam must not automatically be represented as phishing. The generated corpus therefore contains 3,000 messages: 1,500 safe and 1,500 phishing.

Dataset provenance: the source CSVs were obtained on 24 November 2026 from the public [Phishing-Email-Dataset repository](https://github.com/rokibulroni/Phishing-Email-Dataset), which lists Enron and Nazario source files. The underlying corpora are older and should be described as a research baseline, not a current production threat feed.

Rebuild the curated corpus with:

```powershell
python scripts/build_curated_corpus.py
```

For final-year evaluation, build a documented training dataset from legitimate, license-compatible public sources. Keep the source, license, number of messages, class balance, preprocessing steps, and train/validation/test split in the final report.

Recommended workflow:

1. Obtain approved phishing and legitimate email corpora.
2. Remove duplicate messages and personal information where required.
3. Normalize them with `scripts/prepare_dataset.py`.
4. Hold out a final test set before any feature/model selection.
5. Replace `sample_emails.csv` only after saving a dated copy of the original data and recording dataset provenance.

Example:

```powershell
python scripts/prepare_dataset.py raw/public_email_data.csv data/training_emails.csv --text-column body --label-column category --max-per-class 5000
```
