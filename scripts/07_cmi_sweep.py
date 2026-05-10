"""Compute I(X;Y|Z) for every (X,Y) pair conditioned on every other Z.

For each pair (X,Y):
  marginal MI: I(X;Y)
  conditional: I(X;Y | Z) for each Z in vars \ {X,Y}
  best mediator: argmin_Z I(X;Y|Z)
  drop ratio:  1 - I_min / I_marginal

Excludes the deterministic district↔province pair from "candidate edges"
since district fully determines province by construction (province name is
embedded in district string).

Outputs:
  data/processed/cmi/cmi_long.csv         columns: x, y, z, mi, cmi, drop
  data/processed/cmi/cmi_summary.csv      one row per pair: marginal, min_cmi, best_mediator
  reports/figures/cmi_drop_heatmap.png    drop ratio per (pair, Z)
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cmi import cmi, mi
from _lib import ALL_VARS, ROOT, load_df, setup_korean_font

OUT_DIR = ROOT / "data" / "processed" / "cmi"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR = ROOT / "reports" / "figures"

setup_korean_font()


def main() -> None:
    df = load_df()
    print(f"rows = {df.height:,}, vars = {len(ALL_VARS)}")
    pairs = list(combinations(ALL_VARS, 2))
    long_rows = []
    summary = []

    for k, (x, y) in enumerate(pairs, 1):
        I_xy = mi(df, x, y)
        zs = [v for v in ALL_VARS if v not in (x, y)]
        cmi_per_z = {}
        for z in zs:
            cmi_val = cmi(df, x, y, z)
            cmi_per_z[z] = cmi_val
            drop = 1 - cmi_val / I_xy if I_xy > 0 else 0.0
            long_rows.append({"x": x, "y": y, "z": z, "mi_xy": I_xy,
                              "cmi_xy_z": cmi_val, "drop_ratio": drop})
        best_z = min(cmi_per_z, key=cmi_per_z.get)
        I_min = cmi_per_z[best_z]
        I_max = max(cmi_per_z.values())
        print(f"  [{k:2d}/{len(pairs)}] I({x};{y}) = {I_xy:.4f}   "
              f"min I(.|Z) = {I_min:.4f} via Z={best_z}  drop={1-I_min/max(I_xy,1e-12):.2%}")
        summary.append({
            "x": x, "y": y, "mi_xy": I_xy,
            "best_mediator": best_z, "cmi_min": I_min,
            "cmi_max": I_max,
            "drop_max": 1 - I_min / I_xy if I_xy > 0 else 0.0,
            "drop_min": 1 - I_max / I_xy if I_xy > 0 else 0.0,
        })

    long_df = pd.DataFrame(long_rows)
    long_df.to_csv(OUT_DIR / "cmi_long.csv", index=False)
    summ = pd.DataFrame(summary)
    summ.to_csv(OUT_DIR / "cmi_summary.csv", index=False)

    # ---- heatmap of drop ratio per (pair, Z) ----
    pair_labels = [f"{r.x} ~ {r.y}" for r in summ.sort_values("mi_xy", ascending=False).itertuples()]
    pair_order = [(r.x, r.y) for r in summ.sort_values("mi_xy", ascending=False).itertuples()]
    drop_mat = np.full((len(pair_order), len(ALL_VARS)), np.nan)
    for i, (x, y) in enumerate(pair_order):
        sub = long_df[(long_df.x == x) & (long_df.y == y)].set_index("z")
        for j, z in enumerate(ALL_VARS):
            if z in sub.index:
                drop_mat[i, j] = sub.loc[z, "drop_ratio"]

    fig, ax = plt.subplots(figsize=(11, 14))
    im = ax.imshow(drop_mat, aspect="auto", cmap="RdYlBu_r", vmin=0, vmax=1)
    ax.set_xticks(range(len(ALL_VARS)))
    ax.set_xticklabels(ALL_VARS, rotation=45, ha="right")
    ax.set_yticks(range(len(pair_labels)))
    ax.set_yticklabels(pair_labels, fontsize=7)
    ax.set_title("CMI drop ratio = 1 − I(X;Y|Z)/I(X;Y)\n"
                 "red = Z d-separates (mediated)  ·  blue = Z irrelevant (direct edge candidate)")
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02, label="drop ratio")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "cmi_drop_heatmap.png", dpi=130)
    plt.close(fig)

    print(f"\nWrote {OUT_DIR}/cmi_long.csv ({len(long_df)} rows)")
    print(f"Wrote {OUT_DIR}/cmi_summary.csv")
    print(f"Wrote {FIG_DIR}/cmi_drop_heatmap.png")


if __name__ == "__main__":
    main()
