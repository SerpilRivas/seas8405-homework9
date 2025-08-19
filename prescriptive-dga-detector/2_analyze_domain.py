# 2_analyze_domain.py
import argparse
import os
from pathlib import Path

import h2o
import numpy as np
import pandas as pd
import shap
from utils import extract_features

# GenAI (optional)
try:
    import google.generativeai as genai
except Exception:
    genai = None


def load_mojo(mojo_path: str):
    if not Path(mojo_path).exists():
        raise FileNotFoundError(f"MOJO not found at {mojo_path}")
    return h2o.import_mojo(mojo_path)  # H2O 3.46 supports this


def predict_dga_proba(model, X_df: pd.DataFrame) -> np.ndarray:
    hf = h2o.H2OFrame(X_df[["length", "entropy"]])
    preds = model.predict(hf).as_data_frame()
    if "dga" in preds.columns:
        return preds["dga"].to_numpy()
    prob_cols = [c for c in preds.columns if c != "predict"]
    return preds[prob_cols[-1]].to_numpy()


def shap_explain_single(model, instance_df: pd.DataFrame, background_df: pd.DataFrame) -> dict:
    """
    Robustly handle SHAP output shapes for a single-instance explanation.
    """

    def f(X):
        if isinstance(X, np.ndarray):
            X = pd.DataFrame(X, columns=["length", "entropy"])
        return predict_dga_proba(model, X)

    explainer = shap.KernelExplainer(f, background_df[["length", "entropy"]], link="identity")
    shap_vals = explainer.shap_values(instance_df[["length", "entropy"]], nsamples=100)

    # Normalize to a flat 1D array: (1,2) -> (2,), or list -> array -> ravel
    arr = np.array(shap_vals)
    flat = np.ravel(arr)
    if flat.size < 2:
        raise RuntimeError(f"Unexpected SHAP output shape: {arr.shape}")

    return {"length": float(flat[0]), "entropy": float(flat[1])}


def build_xai_findings(domain: str, feats: dict, p: float, shap_vals: dict) -> str:
    def d(v):
        return "towards 'dga'" if v > 0 else "towards 'legit'"

    return (
        f"- Alert: Potential DGA domain detected.\n"
        f"- Domain: '{domain}'\n"
        f"- AI Model Explanation (from SHAP): {p * 100:.2f}% confidence for 'dga'.\n"
        f"  Contributions:\n"
        f"  - entropy={feats['entropy']:.3f} (SHAP {shap_vals['entropy']:+.3f}, {d(shap_vals['entropy'])})\n"
        f"  - length={feats['length']} (SHAP {shap_vals['length']:+.3f}, {d(shap_vals['length'])})"
    )


def generate_playbook(xai_findings: str, model_name="gemini-1.5-flash") -> str:
    if genai is None:
        return "[WARN] google-generativeai not installed."
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "[WARN] GOOGLE_API_KEY not set."
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    prompt = f"""
You are a senior SOC analyst. Based on the XAI findings below, write a concise, prescriptive
incident response playbook with sections: Title, Triage, Containment, Eradication & Recovery,
Validation, Lessons Learned. Prefer concrete Splunk/Zeek/Suricata/EDR steps.

XAI FINDINGS:
{xai_findings}
""".strip()
    return model.generate_content(prompt).text or "[No text returned]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", required=True)
    ap.add_argument("--mojo", default="model/DGA_Leader.zip")
    ap.add_argument("--train-csv", default="data/dga_dataset_train.csv")
    ap.add_argument("--genai-model", default="gemini-1.5-flash")
    args = ap.parse_args()

    feats = extract_features(args.domain)
    X = pd.DataFrame([{"length": feats["length"], "entropy": feats["entropy"]}])

    h2o.init()
    try:
        model = load_mojo(args.mojo)
        p_dga = float(predict_dga_proba(model, X)[0])
        label = "dga" if p_dga >= 0.5 else "legit"

        print(f"\nDomain: {args.domain}")
        print(f"Features: length={feats['length']}, entropy={feats['entropy']:.3f}")
        print(f"Prediction: {label} (p_dga={p_dga:.4f})\n")

        if label == "dga":
            if not Path(args.train_csv).exists():
                raise FileNotFoundError(
                    "Run 1_train_and_export.py first to create the background CSV."
                )
            bg = pd.read_csv(args.train_csv)[["length", "entropy"]]
            bg = bg.sample(n=min(100, len(bg)), random_state=42)
            shap_vals = shap_explain_single(model, X, bg)
            xai = build_xai_findings(args.domain, feats, p_dga, shap_vals)
            print("=== XAI Findings ===")
            print(xai, "\n")
            print("=== Prescriptive Incident Response Playbook ===")
            print(generate_playbook(xai, model_name=args.genai_model))
        else:
            print("Model classified this domain as 'legit'. No playbook generated.")
    finally:
        h2o.shutdown(prompt=False)


if __name__ == "__main__":
    main()
