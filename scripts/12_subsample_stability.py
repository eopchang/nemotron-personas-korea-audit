"""Subsample stability for the recovered skeleton.

For each of N_SEEDS random subsamples of size N_SUB, recompute marginal MI and
the best single-Z conditional MI for every pair. Aggregate to get:
  - mean / std of marginal MI per pair
  - probability the edge would be classified the same way at this sample size

Output:
  data/processed/cmi/stability.csv     per pair: mean_mi, std_mi, p_direct, p_mediated, p_no_edge
  reports/figures/cmi_stability.png    error-bar plot of marginal MI ranked

This is a sanity check that the N=1M findings are not noise.
"""
from __future__ import annotations

import sys
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cmi import cmi, mi
from _lib import ALL_VARS, ROOT, load_df, setup_korean_font

EPSILON = 0.005
N_SUB = 200_000
N_SEEDS = 5
OUT_DIR = ROOT / "data" / "processed" / "cmi"
FIG_DIR = ROOT / "reports" / "figures"
setup_korean_font()


def classify(m_xy: float, cmi_min: float) -> str:
    if m_xy < EPSILON:
        return "no_edge_marginal"
    if cmi_min < EPSILON:
        return "mediated"
    return "direct"


def main() -> None:
    df = load_df()
    pairs = list(combinations(ALL_VARS, 2))
    rows = []
    for seed in range(N_SEEDS):
        sub = df.sample(n=N_SUB, seed=seed, with_replacement=False)
        print(f"\n=== seed={seed} (N={N_SUB:,}) ===")
        for k, (x, y) in enumerate(pairs, 1):
            m_xy = mi(sub, x, y)
            zs = [v for v in ALL_VARS if v not in (x, y)]
            cmi_per_z = {z: cmi(sub, x, y, z) for z in zs}
            cmi_min = min(cmi_per_z.values())
            klass = classify(m_xy, cmi_min)
            rows.append({"seed": seed, "x": x, "y": y, "mi_xy": m_xy,
                         "cmi_min_single": cmi_min, "klass": klass})
        print(f"  done {len(pairs)} pairs")

    long = pd.DataFrame(rows)
    agg = long.groupby(["x", "y"]).agg(
        mean_mi=("mi_xy", "mean"),
        std_mi=("mi_xy", "std"),
        mean_cmi_min=("cmi_min_single", "mean"),
    ).reset_index()
    klass_counts = long.groupby(["x", "y", "klass"]).size().unstack(fill_value=0)
    for c in ["direct", "mediated", "no_edge_marginal"]:
        if c not in klass_counts.columns:
            klass_counts[c] = 0
    klass_counts = klass_counts.reset_index()
    klass_counts["p_direct"] = klass_counts["direct"] / N_SEEDS
    klass_counts["p_mediated"] = klass_counts["mediated"] / N_SEEDS
    klass_counts["p_no_edge_marginal"] = klass_counts["no_edge_marginal"] / N_SEEDS
    out = agg.merge(klass_counts[["x", "y", "p_direct", "p_mediated", "p_no_edge_marginal"]],
                    on=["x", "y"])
    # tag full-N decision
    full = pd.read_csv(OUT_DIR / "skeleton.csv")[["x", "y", "edge_class"]]
    out = out.merge(full, on=["x", "y"])
    out["stable"] = (
        ((out.edge_class == "direct") & (out.p_direct == 1.0))
        | ((out.edge_class == "mediated") & (out.p_mediated == 1.0))
        | ((out.edge_class == "no_edge_marginal") & (out.p_no_edge_marginal == 1.0))
    )
    out.sort_values("mean_mi", ascending=False, inplace=True)
    out.to_csv(OUT_DIR / "stability.csv", index=False)

    # plot
    fig, ax = plt.subplots(figsize=(10, 14))
    labels = [f"{r.x} ~ {r.y}  [{r.edge_class[:6]}]" for r in out.itertuples()]
    yp = np.arange(len(out))
    colors = ["#2c5fa8" if r.stable else "#e07b39" for r in out.itertuples()]
    # error bars in gray, then color-coded markers on top
    ax.errorbar(out["mean_mi"], yp, xerr=out["std_mi"], fmt="none",
                ecolor="#999999", capsize=2, alpha=0.7)
    for i, r in enumerate(out.itertuples()):
        ax.scatter([r.mean_mi], [i], color=colors[i], s=22, edgecolor="black",
                   linewidth=0.4, zorder=5)
    ax.set_yticks(yp)
    ax.set_yticklabels(labels, fontsize=7)
    ax.invert_yaxis()
    ax.axvline(EPSILON, color="gray", lw=0.6, ls="--", label=f"ε = {EPSILON} nats")
    ax.set_xscale("log")
    ax.set_xlabel("marginal MI (nats, log scale) over %d sub-sample seeds" % N_SEEDS)
    ax.set_title(f"CMI subsample stability  (N={N_SUB:,} per seed, {N_SEEDS} seeds)\n"
                 "blue = stable classification, orange = unstable across seeds")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "cmi_stability.png", dpi=130)
    plt.close(fig)

    n_stable = int(out["stable"].sum())
    print(f"\nStable across {N_SEEDS} seeds: {n_stable}/{len(out)} ({n_stable/len(out):.1%})")
    print("Unstable pairs (changed classification across seeds):")
    for r in out[~out["stable"]].itertuples():
        print(f"  {r.x} ~ {r.y}  full={r.edge_class}  "
              f"p_direct={r.p_direct:.1f} p_mediated={r.p_mediated:.1f} "
              f"p_no_edge={r.p_no_edge_marginal:.1f}  mean_mi={r.mean_mi:.4f}")


if __name__ == "__main__":
    main()
