# Manual Test Plan

## Prereqs
- macOS or Linux
- Python 3.12+
- Java 17 (OpenJDK 17)

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Train (creates ./model/DGA_Leader.zip)
```bash
python 1_train_and_export.py | tee examples/train_run.txt
```

## Analyze — legit example
```bash
python 2_analyze_domain.py --domain google.com | tee examples/google_run.txt
```

## Analyze — DGA example (XAI + playbook)
```bash
python 2_analyze_domain.py --domain kq3v9z7j1x5f8g2h.info | tee examples/dga_run.txt
```

## Attach these artifacts
- examples/google_run.txt
- examples/dga_run.txt
- examples/screenshot_A_legit.png
- examples/screenshot_B_xai.png
- examples/screenshot_C_playbook.png
