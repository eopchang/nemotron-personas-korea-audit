"""Bootstrap confidence intervals for marginal MI and conditional MI.

Row-bootstrap the same N as the observed sample, recompute the statistic, and
quantile the resulting distribution. Tells us how much the MI / CMI estimate
varies under data resampling.

Differs from permutation null:
  - permutation null    -> "is this signal real?"   (significance)
  - bootstrap CI        -> "how precise is our estimate?"  (variance)

Outputs:
  data/processed/cmi/bootstrap_marginal.csv     (55 pairs, MI ± CI)
  data/processed/cmi/bootstrap_conditional.csv  (23 direct edges, CMI ± CI)
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
from _perm import bootstrap_resample, summarize_bootstrap

OUT = ROOT / "data" / "processed" / "cmi"
N_BOOTS = 100
SUBSAMPLE_N = 100_000
SEED = 42


def parse_z(z_str: str) -> list[str]:
    return z_str.split("+")


def boot_marginal(sub: pl.DataFrame, x: str, y: str,
                   n_boots: int, seed_base: int) -> dict:
    obs = mi(sub, x, y)
    boots = np.empty(n_boots, dtype=float)
    for k in range(n_boots):
        rng = np.random.default_rng(seed_base + k)
        b = bootstrap_resample(sub, len(sub), rng)
        boots[k] = mi(b, x, y)
    return {"observed": float(obs), **summarize_bootstrap(boots)}


def boot_conditional(sub: pl.DataFrame, x: str, y: str, z_cols: list[str],
                      n_boots: int, seed_base: int) -> dict:
    obs = cmi(sub, x, y, z_cols)
    boots = np.empty(n_boots, dtype=float)
    for k in range(n_boots):
        rng = np.random.default_rng(seed_base + k)
        b = bootstrap_resample(sub, len(sub), rng)
        boots[k] = cmi(b, x, y, z_cols)
    return {"observed": float(obs), **summarize_bootstrap(boots)}


def main() -> None:
    print(f"Loading data, subsampling to {SUBSAMPLE_N:,} (seed={SEED})...", flush=True)
    df = load_df()
    sub = df.sample(n=SUBSAMPLE_N, seed=SEED, with_replacement=False)

    skel = pd.read_csv(OUT / "skeleton.csv")
    print(f"  {len(skel)} pairs total, {(skel.edge_class == 'direct').sum()} direct", flush=True)

    # ============= Marginal bootstrap =============
    print(f"\n=== Marginal MI bootstrap (n_boots={N_BOOTS}) ===", flush=True)
    t0 = time.time()
    rows = []
    for k, r in enumerate(skel.itertuples(), 1):
        result = boot_marginal(sub, r.x, r.y, N_BOOTS,
                                seed_base=SEED * 5000 + k * 173)
        rows.append({"x": r.x, "y": r.y, "mi_full_data": float(r.mi_xy), **result})
        if k % 5 == 0 or k == len(skel):
            print(f"  [{k:2d}/{len(skel)}] {r.x:18s} ~ {r.y:18s}  "
                  f"obs={result['observed']:.5f}  CI=({result['boot_ci95_lo']:.5f}, "
                  f"{result['boot_ci95_hi']:.5f})  SE={result['boot_se']:.5f}", flush=True)
    pd.DataFrame(rows).to_csv(OUT / "bootstrap_marginal.csv", index=False)
    print(f"  -> {OUT}/bootstrap_marginal.csv  ({time.time() - t0:.1f}s)", flush=True)

    # ============= Conditional bootstrap (direct edges) =============
    direct = skel[skel.edge_class == "direct"].copy()
    print(f"\n=== Conditional CMI bootstrap for {len(direct)} direct edges ===", flush=True)
    t0 = time.time()
    rows = []
    for k, r in enumerate(direct.itertuples(), 1):
        z_cols = parse_z(r.z_star_pair)
        result = boot_conditional(sub, r.x, r.y, z_cols, N_BOOTS,
                                   seed_base=SEED * 7000 + k * 251)
        rows.append({
            "x": r.x, "y": r.y,
            "z_cols": "+".join(z_cols),
            "cmi_min_full_data": float(r.cmi_min_any),
            **result,
        })
        print(f"  [{k:2d}/{len(direct)}] {r.x:18s} ~ {r.y:18s} | {','.join(z_cols):30s}  "
              f"obs={result['observed']:.5f}  CI=({result['boot_ci95_lo']:.5f}, "
              f"{result['boot_ci95_hi']:.5f})", flush=True)
    pd.DataFrame(rows).to_csv(OUT / "bootstrap_conditional.csv", index=False)
    print(f"  -> {OUT}/bootstrap_conditional.csv  ({time.time() - t0:.1f}s)", flush=True)


if __name__ == "__main__":
    main()
