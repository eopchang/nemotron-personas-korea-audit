"""ε sensitivity analysis for the recovered skeleton.

The default analysis used ε = 0.005 nats as the threshold below which
I(X;Y) or I(X;Y|Z) is considered 'effectively zero'. ε is an arbitrary
choice; this script re-classifies every pair under a grid of ε values to
quantify how much the conclusions depend on this threshold.

For each ε in the grid:
  no_edge_marginal  if  I(X;Y) < ε
  mediated          if  min CMI < ε  (under |Z|<=2 conditioning)
  direct            otherwise

Key outputs:
  data/processed/cmi/epsilon_counts.csv     class counts per ε
  data/processed/cmi/epsilon_per_pair.csv   per-pair classification × ε
  data/processed/cmi/epsilon_boundary.csv   pairs whose class changes
  reports/figures/epsilon_sensitivity.png   aggregate counts vs ε
  reports/figures/epsilon_per_pair.png      per-pair matrix view
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import ROOT, setup_korean_font

setup_korean_font()

EPS_GRID = [0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05]
DEFAULT_EPS = 0.005

OUT_DIR = ROOT / "data" / "processed" / "cmi"
FIG_DIR = ROOT / "reports" / "figures"
SKEL = OUT_DIR / "skeleton.csv"

CLASS_ORDER = ["direct", "mediated", "no_edge_marginal"]
CLASS_COLOR = {"direct": "#1f3a93",
               "mediated": "#a05d2c",
               "no_edge_marginal": "#9a9a9a"}
CLASS_SHORT = {"direct": "D", "mediated": "M", "no_edge_marginal": "0"}


def classify(mi: float, cmi_min: float, eps: float) -> str:
    if mi < eps:
        return "no_edge_marginal"
    if cmi_min < eps:
        return "mediated"
    return "direct"


def main() -> None:
    skel = pd.read_csv(SKEL)
    print(f"loaded {len(skel)} pairs from {SKEL}")

    # --- per-pair × ε classification ---
    rows = []
    for eps in EPS_GRID:
        for r in skel.itertuples():
            rows.append({
                "eps": eps, "x": r.x, "y": r.y,
                "mi_xy": r.mi_xy, "cmi_min_any": r.cmi_min_any,
                "klass": classify(r.mi_xy, r.cmi_min_any, eps),
            })
    long = pd.DataFrame(rows)

    # --- aggregate counts per ε ---
    counts = long.groupby(["eps", "klass"]).size().unstack(fill_value=0)
    for c in CLASS_ORDER:
        if c not in counts.columns:
            counts[c] = 0
    counts = counts[CLASS_ORDER]
    counts.to_csv(OUT_DIR / "epsilon_counts.csv")
    print("\nClass counts per ε:")
    print(counts)

    # --- per-pair pivot (rows = pairs sorted by mi_xy desc, cols = ε) ---
    piv = long.pivot_table(
        index=["mi_xy", "x", "y"], columns="eps",
        values="klass", aggfunc="first"
    ).sort_index(level="mi_xy", ascending=False)
    piv.to_csv(OUT_DIR / "epsilon_per_pair.csv")

    # --- boundary pairs: classification changes across ε ---
    boundary = []
    for (mi, x, y), row in piv.iterrows():
        unique = row.dropna().unique()
        if len(unique) > 1:
            boundary.append({
                "x": x, "y": y, "mi_xy": float(mi),
                "cmi_min_any": float(skel[(skel.x == x) & (skel.y == y)]["cmi_min_any"].iloc[0]),
                "n_unique_klasses": int(len(unique)),
                **{f"eps={e:g}": str(row[e]) for e in EPS_GRID},
            })
    boundary_df = pd.DataFrame(boundary).sort_values("mi_xy", ascending=False)
    boundary_df.to_csv(OUT_DIR / "epsilon_boundary.csv", index=False)
    print(f"\nBoundary pairs (classification changes within ε grid): {len(boundary_df)}")
    print(boundary_df[["x", "y", "mi_xy", "cmi_min_any", "n_unique_klasses"]].to_string(index=False))

    # ------------------------------------------------------------
    # Figure 1: aggregate counts vs ε
    # ------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8.5, 5))
    for c in CLASS_ORDER:
        ax.semilogx(counts.index, counts[c], "o-", label=c, color=CLASS_COLOR[c],
                    markersize=8, linewidth=2)
    ax.axvline(DEFAULT_EPS, color="red", ls="--", lw=1.0, alpha=0.7,
               label=f"default ε = {DEFAULT_EPS}")
    ax.set_xlabel("ε threshold (nats, log scale)", fontsize=11)
    ax.set_ylabel("count of pairs (out of 55)", fontsize=11)
    ax.set_title("Skeleton classification stability under ε threshold", fontsize=12)
    ax.legend(loc="center right", fontsize=10)
    ax.grid(True, which="both", alpha=0.3)
    ax.set_ylim(0, 55)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "epsilon_sensitivity.png", dpi=130)
    plt.close(fig)

    # ------------------------------------------------------------
    # Figure 2: per-pair matrix
    # ------------------------------------------------------------
    color_idx = {"direct": 0, "mediated": 1, "no_edge_marginal": 2}
    arr = piv.map(lambda v: color_idx[v]).values

    fig, ax = plt.subplots(figsize=(10, 16))
    cmap = plt.matplotlib.colors.ListedColormap(
        [CLASS_COLOR["direct"], CLASS_COLOR["mediated"], CLASS_COLOR["no_edge_marginal"]]
    )
    im = ax.imshow(arr, aspect="auto", cmap=cmap, vmin=-0.5, vmax=2.5)

    ax.set_xticks(range(len(piv.columns)))
    ax.set_xticklabels([f"{e:.4g}" for e in piv.columns], fontsize=9)
    ax.set_xlabel("ε (nats)", fontsize=11)

    pair_labels = [f"{x} ~ {y}  (MI={mi:.4f})" for (mi, x, y) in piv.index]
    ax.set_yticks(range(len(piv)))
    ax.set_yticklabels(pair_labels, fontsize=7)

    # mark default ε column
    default_col = list(piv.columns).index(DEFAULT_EPS)
    ax.axvline(default_col, color="red", lw=1.5, alpha=0.8)
    ax.text(default_col, -1.5, "default\nε=0.005", ha="center", color="red", fontsize=8)

    # text labels
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            v = int(arr[i, j])
            label = ["D", "M", "0"][v]
            ax.text(j, i, label, ha="center", va="center", fontsize=7,
                    color="white" if v in (0, 1) else "black")

    # legend via patches
    import matplotlib.patches as mpatches
    handles = [mpatches.Patch(color=CLASS_COLOR[c], label=c) for c in CLASS_ORDER]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.01, 1.0),
              fontsize=9, frameon=False)

    ax.set_title("Per-pair classification across ε values\n"
                 "(rows sorted by marginal MI desc; D = direct, M = mediated, 0 = no_edge_marginal)",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "epsilon_per_pair.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    # ------------------------------------------------------------
    # Figure 3: housing-related pairs zoom (key falsification check)
    # ------------------------------------------------------------
    housing_mask = (long.x.str.contains("housing")) | (long.y.str.contains("housing"))
    h = long[housing_mask].copy()
    h_piv = h.pivot_table(index=["mi_xy", "x", "y"], columns="eps",
                          values="klass", aggfunc="first").sort_index(level="mi_xy", ascending=False)
    h_arr = h_piv.map(lambda v: color_idx[v]).values

    fig, ax = plt.subplots(figsize=(9, 0.4 * len(h_piv) + 2))
    im = ax.imshow(h_arr, aspect="auto", cmap=cmap, vmin=-0.5, vmax=2.5)
    ax.set_xticks(range(len(h_piv.columns)))
    ax.set_xticklabels([f"{e:.4g}" for e in h_piv.columns], fontsize=9)
    ax.set_yticks(range(len(h_piv)))
    ax.set_yticklabels([f"{x} ~ {y}  (MI={mi:.4f})" for (mi, x, y) in h_piv.index], fontsize=8)
    default_col = list(h_piv.columns).index(DEFAULT_EPS)
    ax.axvline(default_col, color="red", lw=1.5, alpha=0.8)
    for i in range(h_arr.shape[0]):
        for j in range(h_arr.shape[1]):
            v = int(h_arr[i, j])
            label = ["D", "M", "0"][v]
            ax.text(j, i, label, ha="center", va="center", fontsize=8,
                    color="white" if v in (0, 1) else "black")
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=9, frameon=False)
    ax.set_title("Housing-related pairs across ε  (housing decoupling stability check)", fontsize=11)
    ax.set_xlabel("ε (nats)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "epsilon_housing.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    print(f"\nWrote:")
    print(f"  {OUT_DIR}/epsilon_counts.csv")
    print(f"  {OUT_DIR}/epsilon_per_pair.csv")
    print(f"  {OUT_DIR}/epsilon_boundary.csv")
    print(f"  {FIG_DIR}/epsilon_sensitivity.png")
    print(f"  {FIG_DIR}/epsilon_per_pair.png")
    print(f"  {FIG_DIR}/epsilon_housing.png")


if __name__ == "__main__":
    main()
