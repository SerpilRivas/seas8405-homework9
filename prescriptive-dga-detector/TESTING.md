# TESTING.md — Manual Verification

This guide shows how to validate the end-to-end pipeline (AutoML → SHAP → GenAI).

## 1) Setup
From the repo root:
```bash
cd prescriptive-dga-detector
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export GOOGLE_API_KEY="<YOUR-KEY-HERE>"
```

## 2) Train once (if model missing)
```bash
python 1_train_and_export.py
```
Expect to see the files: data/dga_dataset_train.csv, model/DGA_Leader.zip, model/leaderboard.csv.

## 3) Test a known legit domain
```bash
python 2_analyze_domain.py --domain google.com | tee examples/google_run.txt
```
✅ **Pass criteria:** output contains `Prediction: legit` and `No playbook generated`.

## 4) Test a known DGA-like domain
```bash
python 2_analyze_domain.py --domain kq3v9z7j1x5f8g2h.info | tee examples/dga_run.txt
```
✅ **Pass criteria:** output contains:
 - `Prediction: dga`
 - `=== XAI Findings ===` with entropy/length contributions
 - `=== Prescriptive Incident Response Playbook ===` heading

## Notes
 - If you see H2O version-age or pandas conversion warnings, that's normal.
 - To re-run cleanly, you can restart the shell to clear the virtualenv.
