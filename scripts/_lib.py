"""Shared utilities for Phase 2."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "data"

# All 11 useful variables (drop country which is constant).
# age is treated as a binned categorical.
CAT_VARS = [
    "sex",
    "marital_status",
    "military_status",
    "family_type",
    "housing_type",
    "education_level",
    "bachelors_field",
    "occupation",
    "district",
    "province",
]
ALL_VARS = ["age_bin"] + CAT_VARS

AGE_BREAKS = [19, 25, 35, 45, 55, 65, 75, 85, 100]
AGE_LABELS = ["19-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75-84", "85+"]


def load_df() -> pl.DataFrame:
    files = sorted(RAW.glob("train-*.parquet"))
    df = pl.read_parquet([str(f) for f in files], columns=CAT_VARS + ["age"])
    df = df.with_columns(
        pl.col("age")
        .cut(breaks=AGE_BREAKS[1:-1], labels=AGE_LABELS)
        .cast(pl.String)
        .alias("age_bin")
    )
    return df


def joint_counts(df: pl.DataFrame, x: str, y: str) -> np.ndarray:
    """Returns a 2D numpy array of counts indexed by sorted unique values of x and y."""
    g = df.group_by([x, y]).agg(pl.len().alias("n"))
    pdf = g.to_pandas()
    pivot = pdf.pivot(index=x, columns=y, values="n").fillna(0).astype(np.int64)
    return pivot.values, list(pivot.index), list(pivot.columns)


def entropy(p: np.ndarray) -> float:
    p = p[p > 0]
    return float(-(p * np.log(p)).sum())


def metrics_from_counts(counts: np.ndarray) -> dict:
    """Compute Cramér V, NMI, Theil U(rows->cols) and U(cols->rows), independence-TVD."""
    n = counts.sum()
    if n == 0:
        return {"V": np.nan, "NMI": np.nan, "U_y_given_x": np.nan,
                "U_x_given_y": np.nan, "TVD_indep": np.nan}
    p = counts / n
    px = p.sum(axis=1, keepdims=True)
    py = p.sum(axis=0, keepdims=True)
    indep = px @ py
    # Mutual information (nats)
    with np.errstate(divide="ignore", invalid="ignore"):
        mi_terms = np.where(p > 0, p * (np.log(p) - np.log(np.clip(indep, 1e-300, None))), 0.0)
    mi = float(mi_terms.sum())
    hx = entropy(px.flatten())
    hy = entropy(py.flatten())
    nmi = 2 * mi / (hx + hy) if (hx + hy) > 0 else np.nan
    u_y_given_x = mi / hy if hy > 0 else np.nan  # how much knowing X reduces uncertainty about Y
    u_x_given_y = mi / hx if hx > 0 else np.nan
    # Cramér V via chi-square on counts
    expected = indep * n
    with np.errstate(divide="ignore", invalid="ignore"):
        chi2 = float(np.where(expected > 0, (counts - expected) ** 2 / expected, 0.0).sum())
    r, c = counts.shape
    denom = n * max(min(r - 1, c - 1), 1)
    V = float(np.sqrt(chi2 / denom))
    tvd_indep = 0.5 * float(np.abs(p - indep).sum())
    return {
        "MI_nats": mi,
        "H_x": hx,
        "H_y": hy,
        "NMI": float(nmi) if not np.isnan(nmi) else nmi,
        "V": V,
        "U_y_given_x": float(u_y_given_x) if not np.isnan(u_y_given_x) else u_y_given_x,
        "U_x_given_y": float(u_x_given_y) if not np.isnan(u_x_given_y) else u_x_given_y,
        "TVD_indep": tvd_indep,
        "n_rows": int(r),
        "n_cols": int(c),
        "N": int(n),
    }


def setup_korean_font():
    import matplotlib.pyplot as plt

    for cand in ["AppleGothic", "AppleSDGothicNeo", "Noto Sans CJK KR", "NanumGothic"]:
        try:
            plt.rcParams["font.family"] = cand
            break
        except Exception:
            continue
    plt.rcParams["axes.unicode_minus"] = False
