"""Detailed bivariate visualization for curated pairs.

For each pair (x, y) we produce a 3-panel figure:
  (A) Conditional distribution P(Y | X = x_i)  — 100% stacked bars (rows = X levels)
  (B) PMI heatmap log[ P(x,y) / (P(x)P(y)) ]   — signed: red = over-representation
  (C) Top-15 contingency cells with diff vs independence

Plus a CSV with the joint table and per-cell deviation metrics.

For high-cardinality vars (occupation, district, family_type) we keep the top-K
levels by overall mass and lump the rest into "기타".
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import ROOT, joint_counts, load_df, metrics_from_counts, setup_korean_font

OUT_DIR = ROOT / "data" / "processed" / "bivariate_detail"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR = ROOT / "reports" / "figures" / "bivariate"
FIG_DIR.mkdir(parents=True, exist_ok=True)

setup_korean_font()

# --- curated pairs and their visualization knobs ---
PAIRS: list[dict] = [
    {"x": "sex", "y": "bachelors_field", "topk_y": 11, "x_order": ["남자", "여자"]},
    {"x": "sex", "y": "occupation", "topk_y": 20, "x_order": ["남자", "여자"]},
    {"x": "age_bin", "y": "education_level", "topk_y": 7,
     "x_order": ["19-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75-84", "85+"]},
    {"x": "age_bin", "y": "marital_status", "topk_y": 4,
     "x_order": ["19-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75-84", "85+"]},
    {"x": "age_bin", "y": "occupation", "topk_y": 15,
     "x_order": ["19-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75-84", "85+"]},
    {"x": "province", "y": "housing_type", "topk_y": 6},
    {"x": "education_level", "y": "occupation", "topk_y": 15,
     "x_order": ["무학", "초등학교", "중학교", "고등학교", "2~3년제 전문대학", "4년제 대학교", "대학원"]},
    {"x": "marital_status", "y": "family_type", "topk_y": 12,
     "x_order": ["미혼", "배우자있음", "사별", "이혼"]},
    {"x": "sex", "y": "military_status", "topk_y": 2, "x_order": ["남자", "여자"]},
    {"x": "bachelors_field", "y": "occupation", "topk_y": 15},
]


def reduce_to_topk(df: pl.DataFrame, col: str, k: int) -> pl.DataFrame:
    if df.select(pl.col(col).n_unique()).item() <= k:
        return df
    top = (
        df.group_by(col).agg(pl.len().alias("n")).sort("n", descending=True).head(k)
        .select(col).to_series().to_list()
    )
    return df.with_columns(
        pl.when(pl.col(col).is_in(top)).then(pl.col(col)).otherwise(pl.lit("기타")).alias(col)
    )


def build_table(df: pl.DataFrame, x: str, y: str, topk_y: int,
                x_order: list[str] | None) -> pd.DataFrame:
    sub = df.select([x, y])
    sub = reduce_to_topk(sub, y, topk_y)
    counts, x_idx, y_cols = joint_counts(sub, x, y)
    pdf = pd.DataFrame(counts, index=x_idx, columns=y_cols)
    if x_order is not None:
        keep = [v for v in x_order if v in pdf.index]
        pdf = pdf.reindex(keep)
    # order y by overall mass
    y_order = pdf.sum(axis=0).sort_values(ascending=False).index.tolist()
    if "기타" in y_order:  # push 기타 to end
        y_order = [c for c in y_order if c != "기타"] + ["기타"]
    pdf = pdf[y_order]
    return pdf


def plot_pair(pdf: pd.DataFrame, x: str, y: str, m: dict, fig_path: Path) -> pd.DataFrame:
    n = pdf.values.sum()
    p = pdf.values / n
    px = p.sum(axis=1, keepdims=True)
    py = p.sum(axis=0, keepdims=True)
    indep = px @ py
    cond = p / np.where(px > 0, px, 1)  # P(y|x)
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log(np.where(p > 0, p, np.nan) / np.where(indep > 0, indep, np.nan))

    fig = plt.figure(figsize=(16, max(6, 0.5 * len(pdf) + 4)))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.4, 1.4, 1.0])

    # (A) conditional P(y|x) stacked bars
    ax = fig.add_subplot(gs[0, 0])
    bottom = np.zeros(len(pdf))
    cmap = plt.get_cmap("tab20", len(pdf.columns))
    for j, ycol in enumerate(pdf.columns):
        vals = cond[:, j]
        ax.barh(np.arange(len(pdf))[::-1], vals, left=bottom[::-1], color=cmap(j),
                label=str(ycol)[:18], edgecolor="white", linewidth=0.3)
        bottom = bottom + vals
    ax.set_yticks(np.arange(len(pdf))[::-1])
    ax.set_yticklabels([str(v) for v in pdf.index])
    ax.set_xlim(0, 1)
    ax.set_xlabel(f"P({y} | {x})")
    ax.set_title(f"(A) Conditional distribution\nU({y}|{x}) = {m['U_y_given_x']:.3f}")
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, -0.08), ncol=4, fontsize=7, frameon=False)

    # (B) PMI heatmap
    ax = fig.add_subplot(gs[0, 1])
    vmax = np.nanmax(np.abs(pmi))
    norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    im = ax.imshow(pmi, cmap="RdBu_r", norm=norm, aspect="auto")
    ax.set_xticks(range(len(pdf.columns)))
    ax.set_xticklabels([str(c)[:14] for c in pdf.columns], rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(pdf)))
    ax.set_yticklabels([str(v) for v in pdf.index], fontsize=8)
    for i in range(len(pdf)):
        for j in range(len(pdf.columns)):
            v = pmi[i, j]
            if np.isfinite(v) and abs(v) > 0.4:
                ax.text(j, i, f"{v:+.1f}", ha="center", va="center", fontsize=7,
                        color=("white" if abs(v) > 0.7 * vmax else "black"))
    ax.set_title(f"(B) PMI = log[P(x,y)/P(x)P(y)]\nNMI = {m['NMI']:.3f}, V = {m['V']:.3f}")
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
    ax.set_title(f"(C) Top-15 deviation cells\nTVD_indep = {m['TVD_indep']:.3f}")

    fig.suptitle(f"{x}  ×  {y}   (N={n:,})", fontsize=13, y=1.00)
    fig.tight_layout()
    fig.savefig(fig_path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return cells_df


def main() -> None:
    df = load_df()
    print(f"rows = {df.height:,}")
    summary = []
    for spec in PAIRS:
        x, y = spec["x"], spec["y"]
        topk = spec["topk_y"]
        x_order = spec.get("x_order")
        print(f"  -> {x}  ×  {y}  (topk_y={topk})")
        pdf = build_table(df, x, y, topk, x_order)
        # full metrics from non-truncated joint
        full_counts, _, _ = joint_counts(df, x, y)
        m = metrics_from_counts(full_counts)
        # plot from possibly-truncated
        cells = plot_pair(pdf, x, y, m, FIG_DIR / f"detail_{x}__x__{y}.png")
        cells.to_csv(OUT_DIR / f"cells_{x}__x__{y}.csv", index=False)
        pdf.to_csv(OUT_DIR / f"contingency_{x}__x__{y}.csv")
        summary.append({"x": x, "y": y, **{k: m[k] for k in
                       ("V", "NMI", "U_y_given_x", "U_x_given_y", "TVD_indep")}})
    pd.DataFrame(summary).to_csv(OUT_DIR / "summary.csv", index=False)
    print("Done.")


if __name__ == "__main__":
    main()
