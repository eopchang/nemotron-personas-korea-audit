"""Skeleton recovery via PC-style conditioning.

For each pair (X, Y) we test conditional independence under a sequence of
conditioning sets:
  Level 0: Z = {}            (marginal MI)
  Level 1: Z = {z1}          (every other variable, already done in step 07)
  Level 2: Z = {z_star, z2}  (best single mediator + one more, only for survivors)

Decision rule for the skeleton:
  - 'no_edge_marginal'  if I(X;Y) < EPSILON  (essentially independent already)
  - 'mediated'          if min CMI < EPSILON over any tried Z
  - 'direct'            otherwise

EPSILON = 0.005 nats (effect-size threshold; with N=1M, p-values are vacuous).

Outputs:
  data/processed/cmi/skeleton.json     edges + classification + best mediators
  data/processed/cmi/skeleton.csv      one row per pair with all metrics
"""
from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cmi import cmi
from _lib import ALL_VARS, ROOT, load_df

EPSILON = 0.005   # nats — below this we consider X⊥Y under that conditioning
OUT_DIR = ROOT / "data" / "processed" / "cmi"


def classify(rec: dict) -> str:
    if rec["mi_xy"] < EPSILON:
        return "no_edge_marginal"
    if rec["cmi_min_any"] < EPSILON:
        return "mediated"
    return "direct"


def main() -> None:
    df = load_df()
    print(f"rows = {df.height:,}")
    summ = pd.read_csv(OUT_DIR / "cmi_summary.csv")
    long = pd.read_csv(OUT_DIR / "cmi_long.csv")
    pairs = [(r.x, r.y) for r in summ.itertuples()]

    records = []
    for k, (x, y) in enumerate(pairs, 1):
        m_xy = float(summ[(summ.x == x) & (summ.y == y)]["mi_xy"].iloc[0])
        single = long[(long.x == x) & (long.y == y)]
        cmi_min_single = float(single["cmi_xy_z"].min())
        z_star = single.loc[single["cmi_xy_z"].idxmin(), "z"]

        # If marginal already tiny, skip pair-Z (no edge anyway).
        # Else do pair conditioning: condition on (z_star, z2) for each z2.
        pair_results = {}
        if m_xy >= EPSILON and cmi_min_single >= EPSILON:
            others = [v for v in ALL_VARS if v not in (x, y, z_star)]
            for z2 in others:
                pair_results[f"{z_star}+{z2}"] = cmi(df, x, y, [z_star, z2])

        cmi_min_pair = min(pair_results.values()) if pair_results else cmi_min_single
        z_pair_best = (
            min(pair_results, key=pair_results.get) if pair_results else f"{z_star}"
        )

        cmi_min_any = min(cmi_min_single, cmi_min_pair)
        rec = {
            "x": x, "y": y,
            "mi_xy": m_xy,
            "cmi_min_single": cmi_min_single,
            "z_star_single": z_star,
            "cmi_min_pair": cmi_min_pair,
            "z_star_pair": z_pair_best,
            "cmi_min_any": cmi_min_any,
            "drop_max_any": 1 - cmi_min_any / m_xy if m_xy > 0 else 0.0,
        }
        rec["edge_class"] = classify(rec)
        records.append(rec)
        print(f"  [{k:2d}/{len(pairs)}] {x} ~ {y}  marg={m_xy:.4f}  "
              f"min(|Z|=1)={cmi_min_single:.4f}  min(|Z|=2)={cmi_min_pair:.4f}  "
              f"-> {rec['edge_class']}")

    out = pd.DataFrame(records)
    out.to_csv(OUT_DIR / "skeleton.csv", index=False)
    direct = out[out.edge_class == "direct"][["x", "y", "mi_xy", "cmi_min_any",
                                              "drop_max_any", "z_star_pair"]].to_dict(orient="records")
    mediated = out[out.edge_class == "mediated"][["x", "y", "mi_xy", "cmi_min_any",
                                                  "drop_max_any", "z_star_pair"]].to_dict(orient="records")
    summary = {
        "epsilon_nats": EPSILON,
        "n_pairs": len(records),
        "n_direct": int((out.edge_class == "direct").sum()),
        "n_mediated": int((out.edge_class == "mediated").sum()),
        "n_no_edge_marginal": int((out.edge_class == "no_edge_marginal").sum()),
        "direct_edges": direct,
        "mediated_edges": mediated,
    }
    (OUT_DIR / "skeleton.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nDirect: {summary['n_direct']}, "
          f"Mediated: {summary['n_mediated']}, "
          f"NoMarginal: {summary['n_no_edge_marginal']}")


if __name__ == "__main__":
    main()
