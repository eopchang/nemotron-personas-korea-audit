"""Visualize permutation null + bootstrap CI results.

Three figures:
  reports/figures/perm_null_marginal.png
      scatter: observed MI vs null p95, log-log; diagonal = significance line
  reports/figures/perm_null_conditional.png
      same for direct edges with conditional CMI
  reports/figures/forest_marginal.png
      forest plot: each pair with bootstrap 95% CI + null p95 marker

Run after 15_permutation_null.py and 16_bootstrap_ci.py.
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
OUT = ROOT / "data" / "processed" / "cmi"
FIG = ROOT / "reports" / "figures"


def scatter_obs_vs_null(df: pd.DataFrame, title: str, fname: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 7))
    obs = df["observed"].values
    null = df["null_p95"].values
    ratio = obs / np.where(null > 0, null, 1e-12)

    # Color by ratio (effect-size dominance over null)
    colors = []
    for r in ratio:
        if r >= 10:
            colors.append("#1f3a93")  # robust
        elif r >= 2:
            colors.append("#5e8bcf")  # significant
        else:
            colors.append("#c0392b")  # bias-suspect

    ax.scatter(null, obs, c=colors, s=70, edgecolor="black", linewidth=0.5, alpha=0.85)

    # diagonal lines
    lims = [1e-6, 1e1]
    ax.plot(lims, lims, "k--", lw=0.6, alpha=0.5, label="obs = null_p95")
    ax.plot(lims, [2 * x for x in lims], ":", color="gray", lw=0.6, alpha=0.5,
            label="obs = 2 × null_p95")
    ax.plot(lims, [10 * x for x in lims], ":", color="lightgray", lw=0.6,
            alpha=0.5, label="obs = 10 × null_p95")

    # label outliers (top + bottom)
    df2 = df.copy()
    df2["ratio"] = ratio
    for r in df2.nlargest(8, "ratio").itertuples():
        ax.annotate(f"{r.x[:10]}~{r.y[:10]}",
                    xy=(r.null_p95, r.observed),
                    xytext=(5, 0), textcoords="offset points",
                    fontsize=7, color="black", alpha=0.7)
    for r in df2.nsmallest(8, "ratio").itertuples():
        ax.annotate(f"{r.x[:10]}~{r.y[:10]}",
                    xy=(r.null_p95, r.observed),
                    xytext=(5, -8), textcoords="offset points",
                    fontsize=7, color="darkred", alpha=0.7)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1e-6, 1e1)
    ax.set_ylim(1e-6, 1e1)
    ax.set_xlabel("null distribution p95 (nats)  ← bias / chance floor")
    ax.set_ylabel("observed (nats)")
    ax.set_title(title)
    ax.grid(True, which="both", alpha=0.2)

    # Custom legend
    from matplotlib.patches import Patch
    handles = [
        Patch(color="#1f3a93", label="ratio ≥ 10 (robust)"),
        Patch(color="#5e8bcf", label="ratio 2-10 (significant)"),
        Patch(color="#c0392b", label="ratio < 2 (bias-suspect)"),
    ]
    ax.legend(handles=handles, loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(fname, dpi=130)
    plt.close(fig)


def forest_plot(boot: pd.DataFrame, perm: pd.DataFrame, title: str, fname: Path) -> None:
    """Each pair: bootstrap 95% CI horizontal bar + null_p95 marker."""
    df = boot.merge(perm[["x", "y", "null_p95", "ratio_obs_to_p95"]],
                    on=["x", "y"], how="left")
    df = df.sort_values("observed", ascending=True).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(10, max(8, 0.28 * len(df))))
    y_pos = np.arange(len(df))
    # bootstrap CI bar
    ax.hlines(y_pos, df["boot_ci95_lo"], df["boot_ci95_hi"],
              color="#5e8bcf", lw=2, alpha=0.85, label="bootstrap 95% CI")
    # observed point
    ax.scatter(df["observed"], y_pos, s=35, color="black",
               zorder=5, label="observed")
    # null p95 marker (red x)
    ax.scatter(df["null_p95"], y_pos, marker="x", s=35, color="#c0392b",
               zorder=6, label="null p95")

    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{r.x} ~ {r.y}" for r in df.itertuples()], fontsize=7)
    ax.set_xscale("symlog", linthresh=1e-5)
    ax.set_xlabel("MI (nats, symlog)")
    ax.set_title(title)
    ax.grid(True, axis="x", alpha=0.2)
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    fig.savefig(fname, dpi=130)
    plt.close(fig)


def main() -> None:
    pm = pd.read_csv(OUT / "permutation_null_marginal.csv")
    pc = pd.read_csv(OUT / "permutation_null_conditional.csv")
    bm = pd.read_csv(OUT / "bootstrap_marginal.csv")
    bc = pd.read_csv(OUT / "bootstrap_conditional.csv")

    print("=== Marginal: ratio distribution ===")
    pm["ratio"] = pm["observed"] / np.where(pm["null_p95"] > 0, pm["null_p95"], 1e-12)
    print(pm[["x", "y", "observed", "null_p95", "ratio"]].sort_values("ratio").to_string(index=False))

    print("\n=== Conditional (direct edges): ratio distribution ===")
    pc["ratio"] = pc["observed"] / np.where(pc["null_p95"] > 0, pc["null_p95"], 1e-12)
    print(pc[["x", "y", "z_cols", "observed", "null_p95", "ratio"]].sort_values("ratio").to_string(index=False))

    scatter_obs_vs_null(pm, "Marginal MI: observed vs permutation null p95\n"
                        "(log-log, color = effect-size dominance over null)",
                        FIG / "perm_null_marginal.png")
    scatter_obs_vs_null(pc, "Conditional MI: observed vs permutation null p95\n"
                        "(direct edges only, log-log)",
                        FIG / "perm_null_conditional.png")
    forest_plot(bm, pm, "Marginal MI — bootstrap CI + permutation null p95",
                FIG / "forest_marginal.png")
    forest_plot(bc, pc, "Conditional MI (direct edges) — bootstrap CI + null p95",
                FIG / "forest_conditional.png")

    print("\nWrote:")
    for f in ["perm_null_marginal.png", "perm_null_conditional.png",
              "forest_marginal.png", "forest_conditional.png"]:
        print(f"  {FIG}/{f}")


if __name__ == "__main__":
    main()
