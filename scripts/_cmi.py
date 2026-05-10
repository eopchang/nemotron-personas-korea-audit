"""Conditional mutual information utilities (categorical only).

I(X;Y|Z) = sum_{x,y,z} p(x,y,z) log [ p(x,y,z) p(z) / (p(x,z) p(y,z)) ]

All MIs are returned in NATS. Counts use float64 internally.

For multi-variable conditioning, pass Z as a list; we form the joint 'Z-key' by
string concatenation (cheap and exact for our cardinalities).

Conventions:
  - Variables must be string-typed columns in a polars DataFrame
  - We work eagerly because the full 1M frame fits comfortably in RAM
"""
from __future__ import annotations

from typing import Sequence

import numpy as np
import polars as pl


def _joint_key(df: pl.DataFrame, cols: Sequence[str]) -> pl.Series:
    if len(cols) == 1:
        return df[cols[0]]
    return df.select(pl.concat_str([pl.col(c) for c in cols], separator="\x1f")).to_series()


def mi(df: pl.DataFrame, x: str, y: str) -> float:
    """I(X;Y) in nats."""
    g = df.group_by([x, y]).agg(pl.len().alias("n")).to_pandas()
    pivot = g.pivot(index=x, columns=y, values="n").fillna(0).values.astype(np.float64)
    return _mi_from_2d(pivot)


def _mi_from_2d(counts: np.ndarray) -> float:
    n = counts.sum()
    if n == 0:
        return 0.0
    p = counts / n
    px = p.sum(axis=1, keepdims=True)
    py = p.sum(axis=0, keepdims=True)
    indep = px @ py
    with np.errstate(divide="ignore", invalid="ignore"):
        terms = np.where(p > 0, p * (np.log(p) - np.log(np.clip(indep, 1e-300, None))), 0.0)
    return float(terms.sum())


def cmi(df: pl.DataFrame, x: str, y: str, z: str | Sequence[str]) -> float:
    """I(X; Y | Z) in nats. Z may be a single column name or a list.

    Vectorized via polars groupbys: avoids per-stratum Python loop, which
    dominates for high-cardinality Z (e.g., conditioning on occupation+district).

    I(X;Y|Z) = sum_{x,y,z} p(x,y,z) * log[ p(x,y,z) * p(z) / (p(x,z) * p(y,z)) ]
             = sum_{x,y,z} (n_xyz / N) * log[ (n_xyz * n_z) / (n_xz * n_yz) ]
    """
    z_cols = [z] if isinstance(z, str) else list(z)
    z_key = _joint_key(df, z_cols).alias("__zkey__")
    work = df.select([x, y]).hstack([z_key])

    # All three count tables we need.
    n_xyz = work.group_by(["__zkey__", x, y]).agg(pl.len().alias("n_xyz"))
    n_xz = work.group_by(["__zkey__", x]).agg(pl.len().alias("n_xz"))
    n_yz = work.group_by(["__zkey__", y]).agg(pl.len().alias("n_yz"))
    n_z = work.group_by(["__zkey__"]).agg(pl.len().alias("n_z"))

    joined = (
        n_xyz
        .join(n_xz, on=["__zkey__", x], how="left")
        .join(n_yz, on=["__zkey__", y], how="left")
        .join(n_z, on="__zkey__", how="left")
    )
    total = work.height
    if total == 0:
        return 0.0
    j = joined.with_columns(
        (
            pl.col("n_xyz").cast(pl.Float64) / total
            * (
                (pl.col("n_xyz").cast(pl.Float64) * pl.col("n_z").cast(pl.Float64))
                / (pl.col("n_xz").cast(pl.Float64) * pl.col("n_yz").cast(pl.Float64))
            ).log()
        ).alias("term")
    )
    cmi_val = j.select(pl.col("term").fill_nan(0.0).sum()).item()
    return float(cmi_val)


def entropy(df: pl.DataFrame, x: str | Sequence[str]) -> float:
    """H(X) in nats. X may be a list to compute joint entropy."""
    cols = [x] if isinstance(x, str) else list(x)
    g = df.group_by(cols).agg(pl.len().alias("n")).to_pandas()
    n = g["n"].sum()
    p = g["n"].values / n
    return float(-(p * np.log(p[p > 0])).sum())
