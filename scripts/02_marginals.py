"""Compute marginal distributions for every non-text variable.

Outputs:
  data/processed/marginals/<col>.csv   value, count, share
  data/processed/marginals_summary.json   row count, dtype, n_unique per column
  reports/figures/marginal_<col>.png     bar/hist
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import polars as pl

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "data"
OUT_DIR = ROOT / "data" / "processed" / "marginals"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR = ROOT / "reports" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Treat these as structured (categorical / numeric); everything else is free text.
STRUCTURED_COLS = [
    "sex",
    "age",
    "marital_status",
    "military_status",
    "family_type",
    "housing_type",
    "education_level",
    "bachelors_field",
    "occupation",
    "district",
    "province",
    "country",
]
NUMERIC_COLS = {"age"}

# Korean fonts on macOS
for cand in ["AppleGothic", "AppleSDGothicNeo", "Noto Sans CJK KR", "NanumGothic"]:
    try:
        plt.rcParams["font.family"] = cand
        break
    except Exception:
        continue
plt.rcParams["axes.unicode_minus"] = False


def load_lazy() -> pl.LazyFrame:
    files = sorted(RAW.glob("train-*.parquet"))
    assert files, f"No parquet shards under {RAW}"
    return pl.scan_parquet([str(f) for f in files])


def categorical_marginal(lf: pl.LazyFrame, col: str) -> pl.DataFrame:
    df = (
        lf.group_by(col)
        .agg(pl.len().alias("count"))
        .sort("count", descending=True)
        .collect()
    )
    total = df["count"].sum()
    return df.with_columns((pl.col("count") / total).alias("share"))


def numeric_marginal(lf: pl.LazyFrame, col: str) -> pl.DataFrame:
    df = (
        lf.group_by(col)
        .agg(pl.len().alias("count"))
        .sort(col)
        .collect()
    )
    total = df["count"].sum()
    return df.with_columns((pl.col("count") / total).alias("share"))


def plot_categorical(df: pl.DataFrame, col: str, top: int = 30) -> None:
    head = df.head(top).to_pandas()
    fig, ax = plt.subplots(figsize=(10, max(3, 0.25 * len(head))))
    ax.barh(head[col].astype(str)[::-1], head["share"][::-1])
    ax.set_xlabel("share")
    ax.set_title(f"Marginal: {col}  (n_unique={df.height}, top {len(head)})")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"marginal_{col}.png", dpi=120)
    plt.close(fig)


def plot_numeric(df: pl.DataFrame, col: str) -> None:
    pdf = df.to_pandas()
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(pdf[col], pdf["share"], width=1.0)
    ax.set_xlabel(col)
    ax.set_ylabel("share")
    ax.set_title(f"Marginal: {col}")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"marginal_{col}.png", dpi=120)
    plt.close(fig)


def main() -> None:
    lf = load_lazy()
    schema = lf.collect_schema()
    n_rows = lf.select(pl.len()).collect().item()

    summary = {"n_rows": int(n_rows), "columns": {}}

    for col in STRUCTURED_COLS:
        if col not in schema.names():
            print(f"  [skip] missing column: {col}")
            continue
        print(f"  [marginal] {col}")
        if col in NUMERIC_COLS:
            df = numeric_marginal(lf, col)
            plot_numeric(df, col)
        else:
            df = categorical_marginal(lf, col)
            plot_categorical(df, col)
        df.write_csv(OUT_DIR / f"{col}.csv")
        summary["columns"][col] = {
            "dtype": str(schema[col]),
            "n_unique": int(df.height),
            "top5": df.head(5).to_dicts(),
        }

    # mean / quantiles for age
    if "age" in schema.names():
        stats = lf.select(
            pl.col("age").mean().alias("mean"),
            pl.col("age").std().alias("std"),
            pl.col("age").min().alias("min"),
            pl.col("age").quantile(0.25).alias("p25"),
            pl.col("age").median().alias("p50"),
            pl.col("age").quantile(0.75).alias("p75"),
            pl.col("age").max().alias("max"),
        ).collect().to_dicts()[0]
        summary["age_stats"] = {k: float(v) for k, v in stats.items()}

    with open(ROOT / "data" / "processed" / "marginals_summary.json", "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\nDone. n_rows={n_rows:,}")
    print(f"  CSVs   : {OUT_DIR}")
    print(f"  Figures: {FIG_DIR}")


if __name__ == "__main__":
    main()
