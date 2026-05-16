"""Correct the housing marginal comparison for per-person vs per-household unit mismatch.

The original Phase 1 housing comparison used 통계청 2023 인구주택총조사 일반가구 기준
(per-household) distribution as reference, but the Nemotron data is per-person
(1M rows = 1M individual personas). The proper reference is the per-person
distribution, which is not directly published as a headline statistic.

We estimate it from two published numbers:
  - All-household housing distribution (per household)
  - 1인가구 비중 (35.5%) and 1인가구 housing distribution
  - Total avg household size (≈2.21)

Derived: per-person distribution by re-weighting each household by its size.

Outputs:
  data/processed/housing_unit_correction.json  — derived per-person reference + TVD
  (No figure — small numerical correction)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import ROOT

OUT = ROOT / "data" / "processed" / "housing_unit_correction.json"

# ----------------- inputs (all from 통계청 2023 인구주택총조사 공식 발표) -----------------

HH_TOTAL = {           # per-household distribution, 일반가구 기준
    "아파트":               0.531,
    "단독주택":             0.284,
    "연립·다세대주택":     0.112,
    "주택 이외의 거처":     0.058,
    "비주거용 건물 내 주택": 0.014,
}
HH_ONE_PERSON_SHARE = 0.355   # 1인가구가 전체 일반가구에서 차지하는 비중 (2023)
HH_ONE_PERSON = {              # 1인가구의 거처 분포 (2023 "통계로 보는 1인가구")
    "아파트":               0.349,
    "단독주택":             0.401,
    "연립·다세대주택":     0.117,
    "주택 이외의 거처":     0.117,
    "비주거용 건물 내 주택": 0.016,
}
MEAN_HH_SIZE = 2.21            # 전체 평균 가구원수 (2023)

NEMOTRON_PERSON = {            # Nemotron (개인 단위) marginal — Phase 1 결과
    "아파트":               0.6206,
    "단독주택":             0.1692,
    "연립·다세대주택":     0.1401,  # 다세대 11.4% + 연립 2.6%
    "주택 이외의 거처":     0.0603,
    "비주거용 건물 내 주택": 0.0099,
}


def main() -> None:
    # ---- derive 다인가구 distribution ----
    hh_multi = {
        k: (HH_TOTAL[k] - HH_ONE_PERSON_SHARE * HH_ONE_PERSON[k])
           / (1 - HH_ONE_PERSON_SHARE)
        for k in HH_TOTAL
    }
    mean_multi = (MEAN_HH_SIZE - HH_ONE_PERSON_SHARE * 1) / (1 - HH_ONE_PERSON_SHARE)

    # ---- estimate per-person distribution ----
    person_share = {}
    for k in HH_TOTAL:
        pop_in_one = HH_ONE_PERSON_SHARE * 1 * HH_ONE_PERSON[k]
        pop_in_multi = (1 - HH_ONE_PERSON_SHARE) * mean_multi * hh_multi[k]
        person_share[k] = (pop_in_one + pop_in_multi) / MEAN_HH_SIZE

    tvd_household = 0.5 * sum(abs(NEMOTRON_PERSON[k] - HH_TOTAL[k]) for k in HH_TOTAL)
    tvd_person = 0.5 * sum(abs(NEMOTRON_PERSON[k] - person_share[k]) for k in HH_TOTAL)

    cells = []
    for k in HH_TOTAL:
        cells.append({
            "category": k,
            "nemotron_per_person": NEMOTRON_PERSON[k],
            "ref_per_household": HH_TOTAL[k],
            "ref_per_person_estimated": person_share[k],
            "diff_pp_vs_household": (NEMOTRON_PERSON[k] - HH_TOTAL[k]) * 100,
            "diff_pp_vs_person_est": (NEMOTRON_PERSON[k] - person_share[k]) * 100,
        })

    result = {
        "_motivation": (
            "원래 Phase 1 housing 비교는 Nemotron(개인 단위) vs KOSIS 일반가구(가구 단위)로 "
            "단위가 다른 비교였음. 이 보정은 1인가구 비중·1인가구 거처분포·평균 가구원수를 "
            "이용해 per-person reference 를 추정하고 TVD 를 재계산한다."
        ),
        "method": (
            "(a) 다인가구 분포 = (전체가구 - 1인가구비중×1인가구분포) / (1-1인가구비중)\n"
            "(b) 다인가구 평균 가구원수 = (전체평균 - 1인가구비중) / (1-1인가구비중)\n"
            "(c) per-person share(k) = (1인가구비중·1·1인가구(k) + 다인가구비중·평균·다인가구(k)) / 평균"
        ),
        "inputs": {
            "household_total_2023": HH_TOTAL,
            "one_person_share_2023": HH_ONE_PERSON_SHARE,
            "one_person_housing_2023": HH_ONE_PERSON,
            "mean_household_size_2023": MEAN_HH_SIZE,
            "nemotron_per_person": NEMOTRON_PERSON,
        },
        "derived": {
            "multi_person_housing": hh_multi,
            "multi_person_avg_size": mean_multi,
            "per_person_reference_estimated": person_share,
        },
        "tvd_summary": {
            "tvd_vs_household_ref": tvd_household,
            "tvd_vs_person_ref_est": tvd_person,
            "reduction_share": (tvd_household - tvd_person) / tvd_household,
        },
        "cell_level": cells,
        "interpretation": (
            "원본 TVD=0.12 (가구기준 비교) 중 약 30% 가 단위 mismatch 로 인한 환상. "
            "Per-person 보정 후 TVD≈0.084. 아파트 격차는 +9pp → +3.5pp 로 크게 감소. "
            "단독주택 격차는 -11.5pp → -8.0pp 로 여전히 큰 폭. 즉 housing marginal 신호는 "
            "약화되지만 단독주택에 한해 진짜 격차로 남음."
        ),
        "caveat": (
            "1) Per-person reference 는 공식 발표가 없어 본 분석이 자체 추정. "
            "2) 다인가구 평균을 단일 값(2.88)으로 단순화 (실제로는 거처유형별 다름). "
            "3) NVIDIA 가 어느 reference(가구·인구·주택)를 targeting했는지 불명확. "
            "4) Phase 3 의 housing decoupling 결론은 internal structure 분석이라 본 보정과 무관."
        ),
    }

    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Wrote {OUT}")
    print()
    print(f"TVD vs household-basis (원본):  {tvd_household:.4f}")
    print(f"TVD vs person-basis (보정):     {tvd_person:.4f}")
    print(f"감소율:                          {(tvd_household-tvd_person)/tvd_household*100:.1f}%")
    print()
    print("Per-person 보정 후 셀별 격차:")
    for c in cells:
        print(f"  {c['category']:18s}  Nemotron {c['nemotron_per_person']*100:5.1f}%  "
              f"vs per-person ref {c['ref_per_person_estimated']*100:5.1f}%  "
              f"diff {c['diff_pp_vs_person_est']:+5.1f}pp")


if __name__ == "__main__":
    main()
