"""Generate detailed 3-panel visualization for ALL 55 pairs of 11 variables.

Each pair gets:
  (A) Conditional distribution P(Y | X)
  (B) PMI heatmap
  (C) Top-15 deviation cells

High-cardinality variables are truncated to topK by overall mass per axis,
with the rest lumped into '기타'. Truncation is applied to BOTH axes when each
variable exceeds its TOPK threshold.

Outputs:
  reports/figures/bivariate_all/<x>__x__<y>.png            # 55 figures
  data/processed/bivariate_detail_all/contingency_<x>__x__<y>.csv
  data/processed/bivariate_detail_all/cells_<x>__x__<y>.csv
  data/processed/bivariate_detail_all/index.csv            # which pairs were truncated
"""
from __future__ import annotations

import sys
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (ALL_VARS, AGE_LABELS, ROOT, joint_counts, load_df,
                  metrics_from_counts, setup_korean_font)

OUT_DIR = ROOT / "data" / "processed" / "bivariate_detail_all"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR = ROOT / "reports" / "figures" / "bivariate_all"
FIG_DIR.mkdir(parents=True, exist_ok=True)

setup_korean_font()

# Per-variable topK cap. Variables not listed are kept fully.
TOPK = {
    "occupation": 20,
    "district": 25,
    "family_type": 15,
    "bachelors_field": 11,
    "education_level": 7,
    "housing_type": 6,
    "marital_status": 4,
    "province": 17,
    "age_bin": 8,
    "sex": 2,
    "military_status": 2,
}

# Natural orderings (by domain, not by mass) where it makes sense for the conditional plot.
ORDERS = {
    "age_bin": AGE_LABELS,
    "education_level": ["무학", "초등학교", "중학교", "고등학교",
                         "2~3년제 전문대학", "4년제 대학교", "대학원"],
    "marital_status": ["미혼", "배우자있음", "사별", "이혼"],
    "sex": ["남자", "여자"],
    "military_status": ["비현역", "현역"],
}


def reduce_to_topk(df: pl.DataFrame, col: str, k: int) -> tuple[pl.DataFrame, bool]:
    n_unique = df.select(pl.col(col).n_unique()).item()
    if n_unique <= k:
        return df, False
    top = (
        df.group_by(col).agg(pl.len().alias("n")).sort("n", descending=True).head(k)
        .select(col).to_series().to_list()
    )
    return df.with_columns(
        pl.when(pl.col(col).is_in(top)).then(pl.col(col)).otherwise(pl.lit("기타")).alias(col)
    ), True


def build_table(df: pl.DataFrame, x: str, y: str) -> tuple[pd.DataFrame, dict]:
    sub = df.select([x, y])
    sub, x_trunc = reduce_to_topk(sub, x, TOPK[x])
    sub, y_trunc = reduce_to_topk(sub, y, TOPK[y])
    counts, x_idx, y_cols = joint_counts(sub, x, y)
    pdf = pd.DataFrame(counts, index=x_idx, columns=y_cols)

    # ordering: natural if defined, else by mass
    if x in ORDERS:
        keep = [v for v in ORDERS[x] if v in pdf.index]
        if "기타" in pdf.index and "기타" not in keep:
            keep.append("기타")
        pdf = pdf.reindex(keep)
    else:
        order = pdf.sum(axis=1).sort_values(ascending=False).index.tolist()
        if "기타" in order:
            order = [c for c in order if c != "기타"] + ["기타"]
        pdf = pdf.reindex(order)

    if y in ORDERS:
        keep_c = [v for v in ORDERS[y] if v in pdf.columns]
        if "기타" in pdf.columns and "기타" not in keep_c:
            keep_c.append("기타")
        pdf = pdf[keep_c]
    else:
        order_c = pdf.sum(axis=0).sort_values(ascending=False).index.tolist()
        if "기타" in order_c:
            order_c = [c for c in order_c if c != "기타"] + ["기타"]
        pdf = pdf[order_c]

    return pdf, {"x_truncated": x_trunc, "y_truncated": y_trunc}


def plot_pair(pdf: pd.DataFrame, x: str, y: str, m: dict, info: dict, fig_path: Path) -> pd.DataFrame:
    n = pdf.values.sum()
    p = pdf.values / n
    px = p.sum(axis=1, keepdims=True)
    py = p.sum(axis=0, keepdims=True)
    indep = px @ py
    cond = p / np.where(px > 0, px, 1)
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log(np.where(p > 0, p, np.nan) / np.where(indep > 0, indep, np.nan))

    h = max(6, 0.4 * len(pdf) + 4)
    fig = plt.figure(figsize=(17, h))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.4, 1.4, 1.0])

    # (A) conditional P(y|x)
    ax = fig.add_subplot(gs[0, 0])
    bottom = np.zeros(len(pdf))
    cmap = plt.get_cmap("tab20", max(len(pdf.columns), 3))
    for j, ycol in enumerate(pdf.columns):
        vals = cond[:, j]
        ax.barh(np.arange(len(pdf))[::-1], vals, left=bottom[::-1], color=cmap(j),
                label=str(ycol)[:18], edgecolor="white", linewidth=0.3)
        bottom = bottom + vals
    ax.set_yticks(np.arange(len(pdf))[::-1])
    ax.set_yticklabels([str(v) for v in pdf.index], fontsize=8)
    ax.set_xlim(0, 1)
    ax.set_xlabel(f"P({y} | {x})")
    ax.set_title(f"(A) Conditional dist · U({y}|{x})={m['U_y_given_x']:.3f}")
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, -0.08),
              ncol=min(4, len(pdf.columns)), fontsize=6, frameon=False)

    # (B) PMI heatmap
    ax = fig.add_subplot(gs[0, 1])
    finite_pmi = pmi[np.isfinite(pmi)]
    vmax = float(np.max(np.abs(finite_pmi))) if finite_pmi.size else 1.0
    vmax = max(vmax, 1e-3)
    norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    im = ax.imshow(pmi, cmap="RdBu_r", norm=norm, aspect="auto")
    ax.set_xticks(range(len(pdf.columns)))
    ax.set_xticklabels([str(c)[:14] for c in pdf.columns], rotation=45, ha="right", fontsize=7)
    ax.set_yticks(range(len(pdf)))
    ax.set_yticklabels([str(v) for v in pdf.index], fontsize=7)
    show_text = (len(pdf) * len(pdf.columns)) <= 200
    if show_text:
        for i in range(len(pdf)):
            for j in range(len(pdf.columns)):
                v = pmi[i, j]
                if np.isfinite(v) and abs(v) > 0.4:
                    ax.text(j, i, f"{v:+.1f}", ha="center", va="center", fontsize=6,
                            color=("white" if abs(v) > 0.7 * vmax else "black"))
    ax.set_title(f"(B) PMI · NMI={m['NMI']:.3f}, V={m['V']:.3f}")
    fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)

    # (C) Top-15 deviation cells
    ax = fig.add_subplot(gs[0, 2])
    cells = []
    for i, xv in enumerate(pdf.index):
        for j, yv in enumerate(pdf.columns):
            cells.append({
                "cell": f"{str(xv)[:10]} × {str(yv)[:10]}",
                "n": int(pdf.values[i, j]),
                "p_obs": p[i, j],
                "p_indep": indep[i, j],
                "diff_pp": (p[i, j] - indep[i, j]) * 100,
                "pmi": pmi[i, j],
            })
    cells_df = pd.DataFrame(cells)
    top = cells_df.reindex(cells_df["diff_pp"].abs().sort_values(ascending=False).index).head(15)
    colors = ["#c0392b" if d > 0 else "#2c5fa8" for d in top["diff_pp"]]
    ax.barh(top["cell"][::-1], top["diff_pp"][::-1], color=colors[::-1])
    ax.axvline(0, color="black", lw=0.5)
    ax.set_xlabel("p(observed) − p(independent), pp")
    ax.set_title(f"(C) Top-15 cells · TVD_indep={m['TVD_indep']:.3f}")
    ax.tick_params(axis="y", labelsize=7)

    note = []
    if info["x_truncated"]:
        note.append(f"{x} top-{TOPK[x]} + 기타")
    if info["y_truncated"]:
        note.append(f"{y} top-{TOPK[y]} + 기타")
    suptitle = f"{x}  ×  {y}   (N={n:,})"
    if note:
        suptitle += "   [" + " · ".join(note) + "]"
    fig.suptitle(suptitle, fontsize=12, y=1.00)
    fig.tight_layout()
    fig.savefig(fig_path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return cells_df


def main() -> None:
    df = load_df()
    print(f"rows = {df.height:,}")
    pairs = list(combinations(ALL_VARS, 2))
    print(f"pairs = {len(pairs)}")
    index = []
    for k, (x, y) in enumerate(pairs, 1):
        print(f"  [{k:2d}/{len(pairs)}]  {x}  ×  {y}")
        full_counts, _, _ = joint_counts(df, x, y)
        m = metrics_from_counts(full_counts)
        pdf, info = build_table(df, x, y)
        cells = plot_pair(pdf, x, y, m, info, FIG_DIR / f"{x}__x__{y}.png")
        cells.to_csv(OUT_DIR / f"cells_{x}__x__{y}.csv", index=False)
        pdf.to_csv(OUT_DIR / f"contingency_{x}__x__{y}.csv")
        index.append({
            "x": x, "y": y,
            "n_unique_x_full": int(full_counts.shape[0]),
            "n_unique_y_full": int(full_counts.shape[1]),
            "x_truncated_to": TOPK[x] if info["x_truncated"] else None,
            "y_truncated_to": TOPK[y] if info["y_truncated"] else None,
            **{k: m[k] for k in ("V", "NMI", "U_y_given_x", "U_x_given_y", "TVD_indep")},
        })
    pd.DataFrame(index).to_csv(OUT_DIR / "index.csv", index=False)
    print(f"Done. {len(pairs)} pair figures in {FIG_DIR}")


if __name__ == "__main__":
    main()
