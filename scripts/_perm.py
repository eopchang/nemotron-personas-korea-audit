"""Permutation and bootstrap utilities for CMI significance testing.

Stratified shuffle is the key primitive: to test H0: X ⊥ Y | Z, we permute Y
within each Z-stratum, preserving (X|Z) and (Y|Z) marginals while breaking
the joint dependence.

For high-cardinality Z, we build a sortable composite stratum key and shuffle
within sorted blocks — O(N log N) per call.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np
import polars as pl


def _stratum_key(df: pl.DataFrame, strata_cols: Sequence[str]) -> np.ndarray:
    """Build a single string key per row from one or more strata columns."""
    if len(strata_cols) == 1:
        return df[strata_cols[0]].to_numpy()
    cols = [df[c].to_numpy().astype(str) for c in strata_cols]
    sep = "\x1f"
    return np.array([sep.join(t) for t in zip(*cols)])


def shuffle_unconditional(df: pl.DataFrame, target_col: str,
                          rng: np.random.Generator) -> pl.DataFrame:
    """Shuffle target_col across all rows (no stratification).

    Tests H0: X ⊥ Y by breaking joint dependence while preserving marginals.
    """
    arr = df[target_col].to_numpy().copy()
    rng.shuffle(arr)
    return df.with_columns(pl.Series(target_col, arr))


def shuffle_within_strata(df: pl.DataFrame, target_col: str,
                          strata_cols: str | Sequence[str],
                          rng: np.random.Generator) -> pl.DataFrame:
    """Shuffle target_col within each unique stratum defined by strata_cols.

    Tests H0: X ⊥ Y | Z by preserving P(X|Z), P(Y|Z) but breaking P(X,Y|Z).

    Vectorized via lexsort: order rows by (stratum, random_key) — within each
    stratum the rows end up in random order. Then write back to original
    stratum-sorted positions. O(N log N), no Python loop over strata.
    """
    if isinstance(strata_cols, str):
        strata_cols = [strata_cols]
    arr = df[target_col].to_numpy()
    strata = _stratum_key(df, strata_cols)

    # Order rows by (stratum, random_key): within each stratum, rows are
    # randomly permuted.
    keys = rng.random(len(arr))
    rand_order = np.lexsort((keys, strata))

    # Original stratum-sorted positions (stable so within-stratum order is
    # original input order).
    orig_order = np.argsort(strata, kind="stable")

    # Place arr[rand_order] (same stratum block, random within-stratum order)
    # back at orig_order positions (same stratum block, original within-stratum
    # order in the input). Result: each row gets a random value from its own
    # stratum.
    result = np.empty_like(arr)
    result[orig_order] = arr[rand_order]
    return df.with_columns(pl.Series(target_col, result))


def bootstrap_resample(df: pl.DataFrame, n_per: int | None,
                       rng: np.random.Generator) -> pl.DataFrame:
    """Row-bootstrap: sample n_per rows with replacement.

    Tests estimator variance: how much does our statistic move under
    resampling of the same-size data set?
    """
    n = len(df) if n_per is None else n_per
    idx = rng.integers(0, len(df), size=n)
    return df[idx]


def summarize_null(observed: float, null_samples: np.ndarray) -> dict:
    """Standard summary of a permutation null distribution."""
    null = np.asarray(null_samples, dtype=float)
    null_mean = float(np.mean(null))
    null_std = float(np.std(null, ddof=1))
    p_one_sided = (np.sum(null >= observed) + 1) / (len(null) + 1)
    z = (observed - null_mean) / max(null_std, 1e-12)
    ratio = observed / max(np.quantile(null, 0.95), 1e-12)
    return {
        "observed": float(observed),
        "null_mean": null_mean,
        "null_std": null_std,
        "null_p50": float(np.quantile(null, 0.50)),
        "null_p95": float(np.quantile(null, 0.95)),
        "null_p99": float(np.quantile(null, 0.99)),
        "null_max": float(np.max(null)),
        "p_value": float(p_one_sided),
        "z_score": float(z),
        "ratio_obs_to_p95": float(ratio),
        "n_perms": int(len(null)),
    }


def summarize_bootstrap(boot_samples: np.ndarray) -> dict:
    """Standard summary of a bootstrap distribution."""
    boot = np.asarray(boot_samples, dtype=float)
    return {
        "boot_mean": float(np.mean(boot)),
        "boot_se": float(np.std(boot, ddof=1)),
        "boot_ci95_lo": float(np.quantile(boot, 0.025)),
        "boot_ci95_hi": float(np.quantile(boot, 0.975)),
        "boot_median": float(np.quantile(boot, 0.50)),
        "n_boots": int(len(boot)),
    }
