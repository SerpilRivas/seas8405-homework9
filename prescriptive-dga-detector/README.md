# Prescriptive DGA Detector

A tiny demo that trains an **H2O AutoML** model to detect DGA-looking domains, then explains each decision with **SHAP** and (optionally) generates a **prescriptive incident-response playbook** via Gemini.

---

## What it does

1. **Train** a model on simple features (`length`, `entropy`) and export a fast MOJO.
2. **Score** any domain with the MOJO.
3. **Explain** the decision for a suspicious domain with SHAP.
4. **(Optional)** Generate a prescriptive SOC playbook using Gemini (if `GOOGLE_API_KEY` is set).

---

## Requirements

- macOS or Linux
- **Python 3.12+**
- **Java 17** (required by H2O)
- `pip`

Check:
```bash
python3 --version
java -version
```

## Artifacts (what to submit)
**Screenshots**
- `examples/screenshot_A_legit.png` — legit classification (google.com)
- `examples/screenshot_B_xai.png` — XAI findings block for DGA
- `examples/screenshot_C_playbook.png` — first screen of the playbook

**Saved console output**
- `examples/google_run.txt`
- `examples/dga_run.txt`
- `examples/playbook_first_screen.txt`
- `examples/xai_block.txt`
