"""Compute pairwise association metrics for all 11 useful variables.

Metrics:
  - Cramér's V (symmetric)
  - NMI (symmetric, 2*I/(H_x+H_y))
  - Theil's U(Y|X) (asymmetric, I/H_y)  -- 'how much X explains Y'
  - TVD vs independence (symmetric, in [0,1])
  - Mutual Information (nats, raw)

Outputs:
  data/processed/bivariate/metrics_long.csv
  data/processed/bivariate/matrix_<metric>.csv  (square matrices)
  reports/figures/heatmap_<metric>.png

For Theil's U the heatmap reads "row -> col": cell (i,j) = U(j | i) = how much
knowing variable i reduces uncertainty about variable j. So a row of high values
means that variable strongly predicts many others; a column of high values means
that variable is well-explained by many others.
"""
from __future__ import annotations

import json
import sys
from itertools import combinations, product
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import ALL_VARS, ROOT, joint_counts, load_df, metrics_from_counts, setup_korean_font

OUT_DIR = ROOT / "data" / "processed" / "bivariate"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR = ROOT / "reports" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

setup_korean_font()


def main() -> None:
    print(f"Loading data...")
    df = load_df()
    print(f"  rows = {df.height:,}, vars = {len(ALL_VARS)}")

    # init matrices
    V = pd.DataFrame(np.eye(len(ALL_VARS)), index=ALL_VARS, columns=ALL_VARS)
    NMI = pd.DataFrame(np.eye(len(ALL_VARS)), index=ALL_VARS, columns=ALL_VARS)
    U = pd.DataFrame(np.eye(len(ALL_VARS)), index=ALL_VARS, columns=ALL_VARS)  # asym
    T = pd.DataFrame(np.zeros((len(ALL_VARS), len(ALL_VARS))), index=ALL_VARS, columns=ALL_VARS)
    long_rows = []

    pairs = list(combinations(ALL_VARS, 2))
    for k, (x, y) in enumerate(pairs, 1):
        print(f"  [{k}/{len(pairs)}]  {x}  ~  {y}")
        counts, _, _ = joint_counts(df, x, y)
        m = metrics_from_counts(counts)
        V.loc[x, y] = V.loc[y, x] = m["V"]
        NMI.loc[x, y] = NMI.loc[y, x] = m["NMI"]
        T.loc[x, y] = T.loc[y, x] = m["TVD_indep"]
        # U is asymmetric: U.loc[i, j] = U(j | i)
        U.loc[x, y] = m["U_y_given_x"]
        U.loc[y, x] = m["U_x_given_y"]
        long_rows.append({"x": x, "y": y, **m})

    pd.DataFrame(long_rows).to_csv(OUT_DIR / "metrics_long.csv", index=False)
    V.to_csv(OUT_DIR / "matrix_cramers_v.csv")
    NMI.to_csv(OUT_DIR / "matrix_nmi.csv")
    U.to_csv(OUT_DIR / "matrix_theils_u.csv")
    T.to_csv(OUT_DIR / "matrix_tvd_indep.csv")

    # ----- heatmaps -----
    for name, mat, title, vmax, sym in [
        ("cramers_v", V, "Cramér's V (symmetric)", 1.0, True),
        ("nmi", NMI, "NMI = 2I/(H_x+H_y)", 1.0, True),
        ("theils_u", U, "Theil's U(col | row) — knowing row explains X% of col", 1.0, False),
        ("tvd_indep", T, "TVD( joint || marginals product )", 1.0, True),
    ]:
        plot_heatmap(mat, title, FIG_DIR / f"heatmap_{name}.png", vmax=vmax, symmetric=sym)

    summary = {
        "n_rows": int(df.height),
        "vars": ALL_VARS,
        "n_pairs": len(pairs),
        "outputs": {
            "long": "data/processed/bivariate/metrics_long.csv",
            "matrices": [f"data/processed/bivariate/matrix_{m}.csv"
                         for m in ("cramers_v", "nmi", "theils_u", "tvd_indep")],
        },
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nDone. metrics_long has {len(long_rows)} pairs.")


def plot_heatmap(mat: pd.DataFrame, title: str, out: Path, vmax: float, symmetric: bool) -> None:
    fig, ax = plt.subplots(figsize=(10, 8))
    arr = mat.values.copy()
    if symmetric:
        np.fill_diagonal(arr, np.nan)
    im = ax.imshow(arr, cmap="viridis", vmin=0, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(mat.columns)))
    ax.set_yticks(range(len(mat.index)))
    ax.set_xticklabels(mat.columns, rotation=45, ha="right")
    ax.set_yticklabels(mat.index)
    for i in range(len(mat.index)):
        for j in range(len(mat.columns)):
            v = mat.values[i, j]
            if symmetric and i == j:
                continue
            color = "white" if v < 0.5 * vmax else "black"
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", color=color, fontsize=8)
    ax.set_title(title)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()
