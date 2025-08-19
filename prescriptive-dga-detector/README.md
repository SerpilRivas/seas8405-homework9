# Prescriptive DGA Detector

End-to-end pipeline that:
1) trains a high-performance DGA detector with **H2O AutoML**,  
2) explains each decision with **SHAP**, and  
3) turns those explanations into an analyst **playbook** via **Generative AI**.

## Architecture (AutoML → SHAP → GenAI)

- **Ingest**: a domain (`--domain example.com`)
- **Feature engineering**: `length`, `entropy`
- **Predict**: production MOJO model (`model/DGA_Leader.zip`)
- **Explain (local)**: SHAP values for the single prediction
- **XAI → GenAI bridge**: programmatically summarize SHAP into `xai_findings`
- **Prescribe**: prompt the LLM to generate a context-aware incident response playbook

## Quickstart

From this folder:
```bash
cd prescriptive-dga-detector
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python 1_train_and_export.py
# outputs:
#   data/dga_dataset_train.csv
#   model/DGA_Leader.zip
#   model/leaderboard.csv

python 2_analyze_domain.py --domain google.com
## (Optional) Enable Playbook Generation

To let the script ask Gemini to generate an incident-response playbook, set an API key:

```bash
export GOOGLE_API_KEY="<YOUR-KEY-HERE>"
export GOOGLE_API_KEY="<YOUR-KEY-HERE>"
GOOGLE_API_KEY="<YOUR-KEY-HERE>" python prescriptive-dga-detector/2_analyze_domain.py --domain google.com
cd prescriptive-dga-detector
