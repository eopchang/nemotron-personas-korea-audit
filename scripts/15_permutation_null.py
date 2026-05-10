"""Permutation null distribution for marginal MI and conditional MI.

Tests:
  H0_marginal:    X ⊥ Y       (shuffle Y across all rows)
  H0_conditional: X ⊥ Y | Z   (shuffle Y within Z strata)

For each pair we report:
  observed       : MI / CMI on the same subsample
  null_mean      : average MI / CMI under H0
  null_p95       : 95th percentile of null distribution
  p_value        : (#null >= observed + 1) / (n_perms + 1)
  z_score        : (observed - null_mean) / null_std
  ratio_p95      : observed / null_p95   ← effect-size dominance

Why this matters: high-cardinality contingency tables (occupation × district,
where one var has 2,120 unique values) inflate the plug-in MI estimator due to
sparse-cell bias. The permutation null measures *exactly* how much MI we would
expect under independence at the same N and cardinality, so observed - null
gives a bias-corrected effect estimate.

Outputs:
  data/processed/cmi/permutation_null_marginal.csv     (55 pairs)
  data/processed/cmi/permutation_null_conditional.csv  (23 direct edges)
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cmi import cmi, mi
from _lib import ROOT, load_df
from _perm import shuffle_unconditional, shuffle_within_strata, summarize_null

OUT = ROOT / "data" / "processed" / "cmi"
N_PERMS = 100
SUBSAMPLE_N = 100_000
SEED = 42


def parse_z(z_str: str) -> list[str]:
    """Parse 'family_type+education_level' or 'family_type' into a list."""
    return z_str.split("+")


def perm_test_marginal(sub: pl.DataFrame, x: str, y: str,
                        n_perms: int, seed_base: int) -> dict:
    obs = mi(sub, x, y)
    nulls = np.empty(n_perms, dtype=float)
    for k in range(n_perms):
        rng = np.random.default_rng(seed_base + k)
        shuffled = shuffle_unconditional(sub, y, rng)
        nulls[k] = mi(shuffled, x, y)
    return summarize_null(obs, nulls)


def perm_test_conditional(sub: pl.DataFrame, x: str, y: str,
                           z_cols: list[str], n_perms: int,
                           seed_base: int) -> dict:
    obs = cmi(sub, x, y, z_cols)
    nulls = np.empty(n_perms, dtype=float)
    for k in range(n_perms):
        rng = np.random.default_rng(seed_base + k)
        shuffled = shuffle_within_strata(sub, y, z_cols, rng)
        nulls[k] = cmi(shuffled, x, y, z_cols)
    return summarize_null(obs, nulls)


def main() -> None:
    print(f"Loading data, subsampling to {SUBSAMPLE_N:,} (seed={SEED})...")
    df = load_df()
    sub = df.sample(n=SUBSAMPLE_N, seed=SEED, with_replacement=False)

    skel = pd.read_csv(OUT / "skeleton.csv")
    print(f"  {len(skel)} pairs total, "
          f"{(skel.edge_class == 'direct').sum()} direct edges")

    # ============= Marginal null for all 55 pairs =============
    print(f"\n=== Marginal permutation null (n_perms={N_PERMS}) ===")
    t0 = time.time()
    rows = []
    for k, r in enumerate(skel.itertuples(), 1):
        result = perm_test_marginal(sub, r.x, r.y, N_PERMS,
                                     seed_base=SEED * 1000 + k * 137)
        rows.append({
            "x": r.x, "y": r.y,
            "mi_full_data": float(r.mi_xy),
            **result,
        })
        if k % 5 == 0 or k == len(skel):
            print(f"  [{k:2d}/{len(skel)}] {r.x:18s} ~ {r.y:18s}  "
                  f"obs={result['observed']:.5f}  null_p95={result['null_p95']:.5f}  "
                  f"ratio={result['ratio_obs_to_p95']:.2f}  p={result['p_value']:.3f}")
    marg = pd.DataFrame(rows)
    marg.to_csv(OUT / "permutation_null_marginal.csv", index=False)
    print(f"  -> {OUT}/permutation_null_marginal.csv  ({time.time() - t0:.1f}s)")

    # ============= Conditional null for direct edges =============
    direct = skel[skel.edge_class == "direct"].copy()
    print(f"\n=== Conditional permutation null for {len(direct)} direct edges ===")
    t0 = time.time()
    rows = []
    for k, r in enumerate(direct.itertuples(), 1):
        z_cols = parse_z(r.z_star_pair)
        result = perm_test_conditional(sub, r.x, r.y, z_cols, N_PERMS,
                                        seed_base=SEED * 2000 + k * 211)
        rows.append({
            "x": r.x, "y": r.y,
            "z_cols": "+".join(z_cols),
            "cmi_min_full_data": float(r.cmi_min_any),
            **result,
        })
        print(f"  [{k:2d}/{len(direct)}] {r.x:18s} ~ {r.y:18s} | {','.join(z_cols):30s}  "
              f"obs={result['observed']:.5f}  null_p95={result['null_p95']:.5f}  "
              f"ratio={result['ratio_obs_to_p95']:.2f}  p={result['p_value']:.3f}")
    cond = pd.DataFrame(rows)
    cond.to_csv(OUT / "permutation_null_conditional.csv", index=False)
    print(f"  -> {OUT}/permutation_null_conditional.csv  ({time.time() - t0:.1f}s)")

    # ============= Quick interpretation summary =============
    print("\n=== Marginal: significant edges (ratio_obs_to_p95 > 2) ===")
    sig = marg[marg.ratio_obs_to_p95 > 2.0].sort_values("ratio_obs_to_p95", ascending=False)
    print(f"  {len(sig)}/{len(marg)} marginal pairs survive ratio>2 (effect size > bias floor)")

    print("\n=== Marginal: low-ratio pairs (ratio < 2) — possibly bias-dominated ===")
    weak = marg[marg.ratio_obs_to_p95 <= 2.0].sort_values("observed", ascending=False)
    for r in weak.itertuples():
        print(f"  {r.x:18s} ~ {r.y:18s}  obs={r.observed:.5f}  null_p95={r.null_p95:.5f}  ratio={r.ratio_obs_to_p95:.2f}")

    print("\n=== Conditional: 'direct edges' that survive (ratio>2) ===")
    cond_sig = cond[cond.ratio_obs_to_p95 > 2.0].sort_values("ratio_obs_to_p95", ascending=False)
    print(f"  {len(cond_sig)}/{len(cond)} 'direct edges' survive permutation null with ratio>2")

    print("\n=== Conditional: 'direct edges' that DON'T survive (ratio<=2) — suspects ===")
    cond_weak = cond[cond.ratio_obs_to_p95 <= 2.0].sort_values("observed", ascending=False)
    for r in cond_weak.itertuples():
        print(f"  {r.x:18s} ~ {r.y:18s} | {r.z_cols:30s}  obs={r.observed:.5f}  null_p95={r.null_p95:.5f}  ratio={r.ratio_obs_to_p95:.2f}")


if __name__ == "__main__":
    main()
