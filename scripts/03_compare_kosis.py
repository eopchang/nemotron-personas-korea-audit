"""Compare Nemotron synthetic marginals to KOSIS / 통계청 reference values.

For each variable in `data/reference/kosis_reference.json`, compute:
  - TVD (Total Variation Distance) = 0.5 * sum |p_synth - p_ref|
  - L_inf  = max |p_synth - p_ref|
  - chi-square goodness-of-fit (with N=1,000,000 expected counts from ref)
  - per-category absolute diff in percentage points

Output:
  data/processed/kosis_comparison.json
  reports/tables/kosis_comparison.md
  reports/figures/compare_<var>.png  (side-by-side bar)
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
MARG_DIR = ROOT / "data" / "processed" / "marginals"
REF_FILE = ROOT / "data" / "reference" / "kosis_reference.json"
OUT_JSON = ROOT / "data" / "processed" / "kosis_comparison.json"
OUT_MD = ROOT / "reports" / "tables" / "kosis_comparison.md"
FIG_DIR = ROOT / "reports" / "figures"

for cand in ["AppleGothic", "AppleSDGothicNeo", "Noto Sans CJK KR"]:
    try:
        plt.rcParams["font.family"] = cand
        break
    except Exception:
        continue
plt.rcParams["axes.unicode_minus"] = False

# Map reference variable name -> synthetic CSV name
SYNTH_FILE = {
    "marital_status": "marital_status.csv",
    "housing_type": "housing_type.csv",
    "province": "province.csv",
    "sex_adult": "sex.csv",
    "education_level": "education_level.csv",
}

# Pre-aggregation rules: synth bucket -> reference bucket
# Used when the synth scheme is finer-grained than the reference.
PRE_AGG = {
    "housing_type": {
        "연립주택": "연립·다세대주택",
        "다세대주택": "연립·다세대주택",
    }
}


def load_synth(var: str) -> pd.Series:
    fname = SYNTH_FILE[var]
    df = pd.read_csv(MARG_DIR / fname)
    col = df.columns[0]
    s = df.set_index(col)["share"]
    if var in PRE_AGG:
        m = PRE_AGG[var]
        new_idx = [m.get(k, k) for k in s.index]
        s = s.groupby(new_idx).sum()
    return s


def metrics(p_synth: pd.Series, p_ref: pd.Series, n: int = 1_000_000) -> dict:
    keys = sorted(set(p_synth.index) | set(p_ref.index))
    s = p_synth.reindex(keys).fillna(0.0).values
    r = p_ref.reindex(keys).fillna(0.0).values
    s = s / s.sum() if s.sum() > 0 else s
    r = r / r.sum() if r.sum() > 0 else r
    diff = s - r
    tvd = 0.5 * np.abs(diff).sum()
    linf = np.abs(diff).max()
    expected = r * n
    observed = s * n
    mask = expected > 5
    chi2 = float(((observed[mask] - expected[mask]) ** 2 / expected[mask]).sum())
    df_chi = int(mask.sum() - 1)
    p_chi = float(1 - stats.chi2.cdf(chi2, df_chi)) if df_chi > 0 else float("nan")
    per_cat = pd.DataFrame(
        {
            "category": keys,
            "synth": s,
            "reference": r,
            "diff_pp": (s - r) * 100,
        }
    ).sort_values("reference", ascending=False)
    return {
        "TVD": float(tvd),
        "L_inf": float(linf),
        "chi2": chi2,
        "chi2_df": df_chi,
        "chi2_pvalue": p_chi,
        "per_category": per_cat,
    }


def plot_compare(var: str, per_cat: pd.DataFrame) -> None:
    df = per_cat.copy()
    fig, ax = plt.subplots(figsize=(10, max(3, 0.5 * len(df))))
    y = np.arange(len(df))
    ax.barh(y - 0.2, df["reference"], height=0.4, label="reference (KOSIS)", color="#888")
    ax.barh(y + 0.2, df["synth"], height=0.4, label="Nemotron synth", color="#3a78c2")
    ax.set_yticks(y)
    ax.set_yticklabels(df["category"])
    ax.invert_yaxis()
    ax.set_xlabel("share")
    ax.set_title(f"Marginal comparison: {var}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"compare_{var}.png", dpi=120)
    plt.close(fig)


def main() -> None:
    with open(REF_FILE) as f:
        refs = json.load(f)

    out = {"_meta": refs.get("_meta", {}), "results": {}}
    md_lines = ["# KOSIS / 통계청 reference 대비 marginal 비교", "",
                "Phase 1: 단변량 충실도. TVD = 0.5·Σ|p_synth − p_ref|.", ""]

    for var, ref_block in refs.items():
        if var.startswith("_") or var not in SYNTH_FILE:
            continue
        ref_share = pd.Series(ref_block["values"], dtype=float)
        synth_share = load_synth(var)
        m = metrics(synth_share, ref_share)
        plot_compare(var, m["per_category"])

        out["results"][var] = {
            "TVD": m["TVD"],
            "L_inf": m["L_inf"],
            "chi2": m["chi2"],
            "chi2_df": m["chi2_df"],
            "chi2_pvalue": m["chi2_pvalue"],
            "reference_meta": {k: ref_block.get(k) for k in ("population", "year", "source", "caveat")},
            "per_category": m["per_category"].round(4).to_dict(orient="records"),
        }

        md_lines += [
            f"## {var}",
            f"- Reference: {ref_block['source']} · {ref_block['population']} · {ref_block['year']}",
            f"- Caveat: {ref_block['caveat']}",
            f"- **TVD = {m['TVD']:.4f}**, L∞ = {m['L_inf']:.4f}, χ² = {m['chi2']:.1f} (df={m['chi2_df']}, p={m['chi2_pvalue']:.2e})",
            "",
            "| category | reference | synth | diff (pp) |",
            "|---|---:|---:|---:|",
        ]
        for r in m["per_category"].itertuples(index=False):
            md_lines.append(
                f"| {r.category} | {r.reference*100:.2f}% | {r.synth*100:.2f}% | {r.diff_pp:+.2f} |"
            )
        md_lines += ["", f"![compare](../figures/compare_{var}.png)", ""]

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    OUT_MD.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
