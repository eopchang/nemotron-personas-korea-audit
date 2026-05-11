"""External validation: synthetic joint distributions vs KOSIS cross-tab reference.

For each (age × marital, age×sex × education, province × housing) cross-tab cell
that we have a public KOSIS / 통계청 reference for, compute the synthetic
distribution at the SAME granularity and compute per-cell diff (pp).

The reference is partial (KOSIS direct API access blocked by SSO; we use
published headline values from press releases). Each cell carries a citation.

Outputs:
  data/processed/kosis_joint_compare.json
  reports/figures/kosis_joint_age_marital.png
  reports/figures/kosis_joint_age_sex_edu.png
  reports/figures/kosis_joint_province_housing.png
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import ROOT, load_df, setup_korean_font

setup_korean_font()
REF_FILE = ROOT / "data" / "reference" / "kosis_joint.json"
OUT_JSON = ROOT / "data" / "processed" / "kosis_joint_compare.json"
FIG_DIR = ROOT / "reports" / "figures"


def decade_label(age: int) -> str | None:
    if age < 20:
        return None  # exclude teens; reference is 20대+
    if age >= 100:
        return None
    d = (age // 10) * 10
    if d <= 80:
        return f"{d}대"
    return "80대+"


def compare_age_marital(df: pl.DataFrame, ref: dict) -> dict:
    """Compare synthetic age×marital cross-tab vs reference at decade granularity."""
    sub = df.with_columns(
        pl.col("age").map_elements(decade_label, return_dtype=pl.String).alias("decade")
    ).filter(pl.col("decade").is_not_null())

    # Per decade × marital × sex
    g = (
        sub.group_by(["decade", "sex"])
        .agg([
            (pl.col("marital_status") == "미혼").sum().alias("n_unmarried"),
            pl.len().alias("n_total"),
        ])
        .sort(["decade", "sex"])
    )
    pdf = g.to_pandas()
    pdf["unmarried_share"] = pdf["n_unmarried"] / pdf["n_total"]

    # Also: decade overall (sex-pooled) unmarried share
    g_all = (
        sub.group_by("decade")
        .agg([
            (pl.col("marital_status") == "미혼").sum().alias("n_unmarried"),
            pl.len().alias("n_total"),
        ])
        .sort("decade")
    )
    pdf_all = g_all.to_pandas()
    pdf_all["unmarried_share"] = pdf_all["n_unmarried"] / pdf_all["n_total"]

    rows = []
    for decade, ref_cells in ref["data"].items():
        # overall
        if "unmarried_overall" in ref_cells:
            sa = pdf_all[pdf_all["decade"] == decade]
            if not sa.empty:
                rows.append({
                    "decade": decade, "sex": "all", "metric": "unmarried_share",
                    "reference": ref_cells["unmarried_overall"],
                    "synth": float(sa.iloc[0]["unmarried_share"]),
                    "diff_pp": (float(sa.iloc[0]["unmarried_share"]) - ref_cells["unmarried_overall"]) * 100,
                    "n_synth": int(sa.iloc[0]["n_total"]),
                })
        # by sex
        for sx, key in [("남자", "unmarried_M"), ("여자", "unmarried_F")]:
            if key in ref_cells:
                sa = pdf[(pdf["decade"] == decade) & (pdf["sex"] == sx)]
                if not sa.empty:
                    rows.append({
                        "decade": decade, "sex": sx, "metric": "unmarried_share",
                        "reference": ref_cells[key],
                        "synth": float(sa.iloc[0]["unmarried_share"]),
                        "diff_pp": (float(sa.iloc[0]["unmarried_share"]) - ref_cells[key]) * 100,
                        "n_synth": int(sa.iloc[0]["n_total"]),
                    })
    return {"comparison_cells": rows, "reference_meta": {k: ref[k] for k in ref if k.startswith("_")}}


def compare_age_sex_education(df: pl.DataFrame, ref: dict) -> dict:
    """Compare synth education distribution among 50대 초반·60대 초반 by sex."""
    bins = {
        "50s_early_M": ((50, 54), "남자"),
        "50s_early_F": ((50, 54), "여자"),
        "60s_early_M": ((60, 64), "남자"),
        "60s_early_F": ((60, 64), "여자"),
    }
    middle_or_below = ["무학", "초등학교", "중학교"]

    rows = []
    for cell, ((lo, hi), sex) in bins.items():
        sub = df.filter(
            (pl.col("age") >= lo) & (pl.col("age") <= hi) & (pl.col("sex") == sex)
        )
        n_total = sub.height
        if n_total == 0:
            continue
        n_mid_below = sub.filter(pl.col("education_level").is_in(middle_or_below)).height
        n_univ_4yr = sub.filter(pl.col("education_level") == "4년제 대학교").height
        synth = {
            "middle_or_below": n_mid_below / n_total,
            "univ_4yr": n_univ_4yr / n_total,
        }
        ref_cells = ref["data"][cell]
        for metric, ref_val in ref_cells.items():
            rows.append({
                "cell": cell, "metric": metric,
                "reference": ref_val,
                "synth": synth.get(metric, np.nan),
                "diff_pp": (synth.get(metric, np.nan) - ref_val) * 100,
                "n_synth": n_total,
            })
    return {"comparison_cells": rows, "reference_meta": {k: ref[k] for k in ref if k.startswith("_")}}


def compare_province_housing(df: pl.DataFrame, ref_apt: dict, ref_det: dict) -> dict:
    """Compare apartment % and detached % per province (synth = person-unit)."""
    g = (
        df.group_by(["province", "housing_type"])
        .agg(pl.len().alias("n"))
        .to_pandas()
    )
    pivot = g.pivot_table(index="province", columns="housing_type", values="n", fill_value=0)
    pivot["total"] = pivot.sum(axis=1)
    apt_share = (pivot["아파트"] / pivot["total"]).to_dict()
    det_share = (pivot["단독주택"] / pivot["total"]).to_dict()

    rows = []
    for prov, ref_val in ref_apt["data"].items():
        if prov == "전국":
            # nation-wide synth
            n_total = df.height
            n_apt = df.filter(pl.col("housing_type") == "아파트").height
            sv = n_apt / n_total
        else:
            sv = apt_share.get(prov, np.nan)
        rows.append({
            "province": prov, "housing_type": "아파트",
            "reference_household_pct": ref_val,
            "synth_person_pct": float(sv) if not np.isnan(sv) else None,
            "diff_pp": (sv - ref_val) * 100 if not np.isnan(sv) else None,
        })
    for prov, ref_val in ref_det["data"].items():
        if prov == "전국":
            n_total = df.height
            n_det = df.filter(pl.col("housing_type") == "단독주택").height
            sv = n_det / n_total
        else:
            sv = det_share.get(prov, np.nan)
        rows.append({
            "province": prov, "housing_type": "단독주택",
            "reference_household_pct": ref_val,
            "synth_person_pct": float(sv) if not np.isnan(sv) else None,
            "diff_pp": (sv - ref_val) * 100 if not np.isnan(sv) else None,
        })
    return {"comparison_cells": rows,
            "reference_meta_apt": {k: ref_apt[k] for k in ref_apt if k.startswith("_")},
            "reference_meta_det": {k: ref_det[k] for k in ref_det if k.startswith("_")}}


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------

def plot_age_marital(rows: list[dict], fname: Path) -> None:
    df = pd.DataFrame(rows)
    df = df.sort_values(["decade", "sex"])

    decades = ["20대", "30대", "40대", "50대"]
    sexes = ["all", "남자", "여자"]
    fig, ax = plt.subplots(figsize=(10, 5))
    width = 0.18
    x = np.arange(len(decades))
    colors = {"all": "#2c5fa8", "남자": "#5e8bcf", "여자": "#c0392b"}
    for i, sx in enumerate(sexes):
        sub = df[df.sex == sx].set_index("decade").reindex(decades)
        # paired bars: reference (light) and synth (dark)
        offset = (i - 1) * width * 1.3
        ref_vals = sub["reference"].values
        synth_vals = sub["synth"].values
        ax.bar(x + offset - width/2, ref_vals, width, color=colors[sx], alpha=0.4,
               label=f"reference {sx}" if sx != "all" else "reference (sex-pooled)")
        ax.bar(x + offset + width/2, synth_vals, width, color=colors[sx], alpha=0.95,
               edgecolor="black", linewidth=0.5,
               label=f"synth {sx}" if sx != "all" else "synth (sex-pooled)")

    ax.set_xticks(x); ax.set_xticklabels(decades)
    ax.set_ylabel("미혼 비율")
    ax.set_title("age × marital: synthetic (개인 단위, 19+) vs KOSIS 2020 census (15+)\n"
                 "투명 = reference, 진함 = synth. 출처: 통계청 + 한국의 사회동향 2024")
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    ax.set_ylim(0, 1.05); ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(fname, dpi=130)
    plt.close(fig)


def plot_age_sex_edu(rows: list[dict], fname: Path) -> None:
    df = pd.DataFrame(rows)
    cells = ["50s_early_M", "50s_early_F", "60s_early_M", "60s_early_F"]
    metrics = ["middle_or_below", "univ_4yr"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, met in zip(axes, metrics):
        sub = df[df.metric == met].set_index("cell").reindex(cells)
        x = np.arange(len(cells))
        ax.bar(x - 0.2, sub["reference"], 0.4, label="reference", color="#888", alpha=0.7)
        ax.bar(x + 0.2, sub["synth"], 0.4, label="synth", color="#2c5fa8")
        ax.set_xticks(x); ax.set_xticklabels(cells, rotation=15)
        ax.set_title(f"{met}")
        ax.legend(); ax.grid(axis="y", alpha=0.3)
    fig.suptitle("age × sex × education: 50s/60s 초반 (50-54, 60-64)\n"
                 "출처: 한국노동사회연구소 / 통계청 인구주택총조사 가공", fontsize=11)
    fig.tight_layout()
    fig.savefig(fname, dpi=130)
    plt.close(fig)


def plot_province_housing(rows: list[dict], fname: Path) -> None:
    df = pd.DataFrame(rows)
    df = df[df.synth_person_pct.notnull()]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, htype in zip(axes, ["아파트", "단독주택"]):
        sub = df[df.housing_type == htype].copy()
        sub = sub.sort_values("reference_household_pct", ascending=False)
        x = np.arange(len(sub))
        ax.bar(x - 0.2, sub["reference_household_pct"], 0.4,
               label="reference (가구 기준)", color="#888", alpha=0.7)
        ax.bar(x + 0.2, sub["synth_person_pct"], 0.4,
               label="synth (개인 기준)", color="#2c5fa8")
        ax.set_xticks(x); ax.set_xticklabels(sub["province"], rotation=20)
        ax.set_title(htype); ax.set_ylabel("비율")
        ax.legend(); ax.grid(axis="y", alpha=0.3)
    fig.suptitle("province × housing_type: synthetic vs 2023 census (보도자료)\n"
                 "단위 차이 (가구 vs 개인) — 직접 차이가 아니라 *방향성* 일치 검증용",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(fname, dpi=130)
    plt.close(fig)


def main() -> None:
    df = load_df()
    with open(REF_FILE) as f:
        ref = json.load(f)
    print(f"loaded synthetic ({df.height:,} rows) and reference")

    out: dict = {"_meta": ref.get("_meta", {})}

    # 1. age × marital
    print("\n=== age × marital_status ===")
    r = compare_age_marital(df, ref["age_marital_decade"])
    out["age_marital"] = r
    for c in r["comparison_cells"]:
        print(f"  {c['decade']:4s} sex={c['sex']:3s}  ref={c['reference']:.4f}  "
              f"synth={c['synth']:.4f}  diff={c['diff_pp']:+.2f}pp  n_synth={c['n_synth']:,}")
    plot_age_marital(r["comparison_cells"], FIG_DIR / "kosis_joint_age_marital.png")

    # 2. age × sex × education
    print("\n=== age × sex × education ===")
    r = compare_age_sex_education(df, ref["age_sex_education"])
    out["age_sex_education"] = r
    for c in r["comparison_cells"]:
        print(f"  {c['cell']:14s}  {c['metric']:20s}  ref={c['reference']:.4f}  "
              f"synth={c['synth']:.4f}  diff={c['diff_pp']:+.2f}pp  n={c['n_synth']:,}")
    plot_age_sex_edu(r["comparison_cells"], FIG_DIR / "kosis_joint_age_sex_edu.png")

    # 3. province × housing
    print("\n=== province × housing_type ===")
    r = compare_province_housing(df, ref["province_housing_apt_pct"], ref["province_housing_detached_pct"])
    out["province_housing"] = r
    for c in r["comparison_cells"]:
        if c["synth_person_pct"] is None:
            print(f"  {c['province']:6s} {c['housing_type']:6s}  ref={c['reference_household_pct']:.4f}  synth=N/A")
        else:
            print(f"  {c['province']:6s} {c['housing_type']:6s}  ref={c['reference_household_pct']:.4f}  "
                  f"synth={c['synth_person_pct']:.4f}  diff={c['diff_pp']:+.2f}pp")
    plot_province_housing(r["comparison_cells"], FIG_DIR / "kosis_joint_province_housing.png")

    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"\nWrote {OUT_JSON}")
    print(f"Wrote 3 figures to {FIG_DIR}")


if __name__ == "__main__":
    main()
