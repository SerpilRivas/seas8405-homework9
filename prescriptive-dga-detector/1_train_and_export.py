import argparse
import os
import random
from pathlib import Path

import h2o
import pandas as pd
from h2o.automl import H2OAutoML
from utils import extract_features

DEF_OUT_CSV = "data/dga_dataset_train.csv"
DEF_MODEL_DIR = "model"
DEF_RUNTIME_SECS = 120  # adjust if you want longer AutoML

LEGIT_SEEDS = [
    "google.com",
    "wikipedia.org",
    "openai.com",
    "h2o.ai",
    "gwu.edu",
    "python.org",
    "microsoft.com",
    "apple.com",
    "github.com",
    "cloudflare.com",
    "reddit.com",
    "nytimes.com",
    "washingtonpost.com",
    "bbc.co.uk",
    "nasa.gov",
    "who.int",
]


def synth_dga(n: int) -> list[str]:
    alph = "abcdefghijklmnopqrstuvwxyz0123456789"
    out = []
    for _ in range(n):
        L = random.randint(15, 30)
        core = "".join(random.choice(alph) for _ in range(L))
        tld = random.choice([".xyz", ".info", ".top", ".online", ".site"])
        out.append(core + tld)
    return out


def make_dataset(domains: list[str], label: str) -> pd.DataFrame:
    rows = []
    for d in domains:
        f = extract_features(d)
        f["domain"] = d
        f["label"] = label
        rows.append(f)
    return pd.DataFrame(rows)


def build_or_load_dataset(args) -> pd.DataFrame:
    Path("data").mkdir(exist_ok=True)
    legit = LEGIT_SEEDS
    dga = synth_dga(len(legit))
    df = pd.concat([make_dataset(legit, "legit"), make_dataset(dga, "dga")], ignore_index=True)
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    df.to_csv(args.output_csv, index=False)
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-csv", default=DEF_OUT_CSV)
    parser.add_argument("--model-dir", default=DEF_MODEL_DIR)
    parser.add_argument("--runtime-secs", type=int, default=DEF_RUNTIME_SECS)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    Path(args.model_dir).mkdir(exist_ok=True)
    df = build_or_load_dataset(args)

    h2o.init()
    try:
        hf = h2o.H2OFrame(df[["length", "entropy", "label"]])
        hf["label"] = hf["label"].asfactor()
        x, y = ["length", "entropy"], "label"
        train, valid = hf.split_frame([0.8], seed=args.seed)

        aml = H2OAutoML(
            max_runtime_secs=args.runtime_secs,
            seed=args.seed,
            balance_classes=True,
            sort_metric="AUC",
        )
        aml.train(x=x, y=y, training_frame=train, validation_frame=valid)

        lb = aml.leaderboard.as_data_frame()
        (Path(args.model_dir) / "leaderboard.csv").write_text(lb.to_csv(index=False))

        leader = aml.leader
        mojo_tmp = leader.download_mojo(path=args.model_dir, get_genmodel_jar=False)
        os.replace(mojo_tmp, Path(args.model_dir) / "DGA_Leader.zip")

        print("[OK] Training complete")
        print(f"- dataset: {args.output_csv}")
        print(f"- model:   {args.model_dir}/DGA_Leader.zip")
    finally:
        h2o.shutdown(prompt=False)


if __name__ == "__main__":
    main()
