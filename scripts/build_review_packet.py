"""Build REVIEW_PACKET.md and key_results.json for external model review.

REVIEW_PACKET.md is a single self-contained document combining:
  - Repo intro + how to interpret
  - All Phase 1/2/3 reports
  - CLAIMS_LEDGER
  - Key numerical results table
  - Methodology summary
  - Glossary (compact)

key_results.json is a structured dump of every important number so a reviewer
can mechanically verify claims.

Run after analysis updates to keep external review materials in sync.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
REVIEW = ROOT / "review"
REVIEW.mkdir(parents=True, exist_ok=True)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else f"(missing: {p})"


def section(title: str, body: str) -> str:
    return f"\n\n---\n\n# {title}\n\n{body}\n"


def build_key_results() -> dict:
    """Collect key numerical results from processed/ files."""
    out = {"_meta": {
        "generated_by": "scripts/build_review_packet.py",
        "purpose": "Single structured dump of all key numbers for external verification",
    }}

    marg = json.loads(read(ROOT / "data/processed/marginals_summary.json"))
    out["dataset_basics"] = {
        "n_rows": marg["n_rows"],
        "age_stats": marg.get("age_stats", {}),
        "n_unique_per_var": {k: v["n_unique"] for k, v in marg["columns"].items()},
    }

    # KOSIS comparison metrics
    kosis = json.loads(read(ROOT / "data/processed/kosis_comparison.json"))
    out["phase1_kosis_comparison"] = {
        var: {
            "TVD": r["TVD"], "L_inf": r["L_inf"],
            "reference": r["reference_meta"],
        }
        for var, r in kosis["results"].items()
    }

    # Bivariate top pairs
    bv = pd.read_csv(ROOT / "data/processed/bivariate/metrics_long.csv")
    bv = bv.sort_values("NMI", ascending=False)
    out["phase2_top15_pairs_by_nmi"] = bv.head(15)[
        ["x", "y", "V", "NMI", "U_y_given_x", "U_x_given_y", "TVD_indep"]
    ].round(4).to_dict(orient="records")
    out["phase2_bottom5_pairs_by_nmi"] = bv.tail(5)[
        ["x", "y", "V", "NMI", "TVD_indep"]
    ].round(6).to_dict(orient="records")

    # Skeleton
    skel = json.loads(read(ROOT / "data/processed/cmi/skeleton.json"))
    out["phase3_skeleton"] = {
        "epsilon_nats": skel["epsilon_nats"],
        "n_pairs": skel["n_pairs"],
        "n_direct": skel["n_direct"],
        "n_mediated": skel["n_mediated"],
        "n_no_edge_marginal": skel["n_no_edge_marginal"],
        "direct_edges": skel["direct_edges"],
        "mediated_edges": skel["mediated_edges"],
    }

    # Within-synthetic predictability check (key name retains legacy "decoupling_probe")
    out["phase3_decoupling_probe"] = json.loads(
        read(ROOT / "data/processed/decoupling_probe.json")
    )

    # Stability
    stab = pd.read_csv(ROOT / "data/processed/cmi/stability.csv")
    out["phase3_stability"] = {
        "n_seeds": 5,
        "n_per_seed": 200000,
        "n_pairs_total": int(len(stab)),
        "n_pairs_stable": int(stab["stable"].sum()),
        "unstable_pairs": stab[~stab["stable"]][
            ["x", "y", "edge_class", "p_direct", "p_mediated", "p_no_edge_marginal"]
        ].to_dict(orient="records"),
    }

    # Node degrees
    deg = pd.read_csv(ROOT / "data/processed/cmi/node_degrees.csv")
    out["phase3_node_degrees_in_skeleton"] = deg.to_dict(orient="records")

    # ε threshold sensitivity (Phase 3 §2.7)
    eps = pd.read_csv(ROOT / "data/processed/cmi/epsilon_counts.csv")
    out["phase3_epsilon_sensitivity"] = {
        "eps_grid": eps["eps"].tolist(),
        "default_eps": 0.005,
        "counts_by_epsilon": {
            str(row["eps"]): {
                "direct": int(row["direct"]),
                "mediated": int(row["mediated"]),
                "no_edge_marginal": int(row["no_edge_marginal"]),
            }
            for _, row in eps.iterrows()
        },
    }

    # Permutation null (Phase 3 §2.5)
    pn_m = pd.read_csv(ROOT / "data/processed/cmi/permutation_null_marginal.csv")
    pn_c = pd.read_csv(ROOT / "data/processed/cmi/permutation_null_conditional.csv")
    out["phase3_permutation_null"] = {
        "n_perms_per_pair": 100,
        "subsample_n": 100_000,
        "metric_key": "ratio_obs_to_p95 (observed / null_p95)",
        "ratio_tier_thresholds": {"robust": 10, "significant": 2},
        "marginal_pairs": pn_m[
            ["x", "y", "observed", "null_p95", "ratio_obs_to_p95", "p_value"]
        ].round(5).to_dict(orient="records"),
        "conditional_direct_edges": pn_c[
            ["x", "y", "z_cols", "observed", "null_p95", "ratio_obs_to_p95", "p_value"]
        ].round(5).to_dict(orient="records"),
    }

    # Bootstrap CI (Phase 3 §2.5)
    bs_m = pd.read_csv(ROOT / "data/processed/cmi/bootstrap_marginal.csv")
    bs_c = pd.read_csv(ROOT / "data/processed/cmi/bootstrap_conditional.csv")
    out["phase3_bootstrap_ci"] = {
        "n_boots_per_pair": 100,
        "subsample_n": 100_000,
        "ci_level": "95%",
        "marginal_pairs": bs_m[
            ["x", "y", "observed", "boot_ci95_lo", "boot_ci95_hi", "boot_se"]
        ].round(5).to_dict(orient="records"),
        "conditional_direct_edges": bs_c[
            ["x", "y", "z_cols", "observed", "boot_ci95_lo", "boot_ci95_hi", "boot_se"]
        ].round(5).to_dict(orient="records"),
    }

    # Leakage check (Phase 3 §1.4)
    out["phase3_decoupling_probe_leakage_check"] = json.loads(
        read(ROOT / "data/processed/decoupling_probe_no_leakage.json")
    )

    # Military breakdown (Phase 3 §3.4)
    out["phase3_military_breakdown"] = json.loads(
        read(ROOT / "data/processed/military_breakdown.json")
    )

    # Housing per-person reference correction (Phase 1 §3-4)
    out["phase1_housing_unit_correction"] = json.loads(
        read(ROOT / "data/processed/housing_unit_correction.json")
    )

    return out


def render_kr(d: dict) -> str:
    return "```json\n" + json.dumps(d, ensure_ascii=False, indent=2) + "\n```"


def main() -> None:
    # 1. key_results.json
    kr = build_key_results()
    (REVIEW / "key_results.json").write_text(
        json.dumps(kr, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote {REVIEW / 'key_results.json'}")

    # 2. REVIEW_PACKET.md
    intro = """# REVIEW PACKET — Nemotron-Personas-Korea Audit

> **외부 리뷰어를 위한 단일 자족 문서.**
> 본 패킷 하나만으로 본 검토의 방법론, 결과, 주장의 증거 사슬을 모두 평가할 수 있도록
> 자동 생성되었습니다. 그림은 별도 (필요 시 `reports/figures/` 참조).
>
> **사용법**: 이 문서 전체를 GPT/Claude/Gemini 등의 long-context 모델에 첨부하고,
> [`REVIEW_PROMPTS.md`](REVIEW_PROMPTS.md) 의 6종 프롬프트 (통합/Falsification/방법론/통계/도메인/재현성) 중 하나로 분석을 요청하세요.

---

## 0. 패킷 구조

본 문서는 다음 순서로 구성됩니다:

§1. 프로젝트 개요 (5분 읽기)
§2. 데이터셋 정보
§3. 방법론 종합
§4. Phase 1 — 단변량 충실도 리포트
§5. Phase 2 — 이변량 결합 리포트
§6. Phase 3 — PGM 구조 추론 리포트
§7. CLAIMS LEDGER (36개 주장 + 증거)
§8. KEY RESULTS (구조화 수치)
§9. KOSIS reference 통계 (검증용)
§10. 한계 및 자기 진술
"""

    parts = [intro]

    # §1 Project intro = README excerpt minus repo navigation noise
    readme = read(ROOT / "README.md")
    intro_excerpt = readme.split("## 🧭 어디부터")[0]  # take TL;DR + key findings
    parts.append(section("§1. 프로젝트 개요", intro_excerpt.replace("# Nemotron-Personas-Korea — 데이터셋 독립 검토", "").strip()))

    # §2 Dataset info compact
    parts.append(section("§2. 데이터셋 정보 (NVIDIA 공식 자료 + 본 리포 실측)",
                        f"""
| 항목 | 값 |
|---|---|
| 이름 | Nemotron-Personas-Korea |
| 공개 | 2026-04-20, HuggingFace |
| 라이선스 | CC BY 4.0 |
| 행 수 | {kr['dataset_basics']['n_rows']:,} |
| age 범위 | {kr['dataset_basics']['age_stats'].get('min', 19)}–{kr['dataset_basics']['age_stats'].get('max', 99)} 세, 평균 {kr['dataset_basics']['age_stats'].get('mean', 0):.2f} |
| 변수별 unique 값 수 | {render_kr(kr['dataset_basics']['n_unique_per_var'])} |
| 생성 도구 | NVIDIA NeMo Data Designer |
| 생성 모델 | PGM (인구통계) + google/gemma-4-31B-it (자연어) |
| 시드 | KOSIS, 대법원, NHIS, KREI, 네이버클라우드 |
"""))

    # §3 Methodology
    parts.append(section("§3. 방법론 종합", read(ROOT / "docs/METHODOLOGY.md").split("\n", 1)[1]))

    # §4–6 Phase reports
    parts.append(section("§4. Phase 1 — 단변량 충실도", read(ROOT / "reports/PHASE1_REPORT.md").split("\n", 1)[1]))
    parts.append(section("§5. Phase 2 — 이변량 결합", read(ROOT / "reports/PHASE2_REPORT.md").split("\n", 1)[1]))
    parts.append(section("§6. Phase 3 — PGM 구조 추론", read(ROOT / "reports/PHASE3_REPORT.md").split("\n", 1)[1]))

    # §7 Claims Ledger
    parts.append(section("§7. CLAIMS LEDGER", read(REVIEW / "CLAIMS_LEDGER.md").split("\n", 1)[1]))

    # §8 Key Results structured
    parts.append(section("§8. KEY RESULTS — 구조화 수치 (수치 검증용)",
                        f"본 섹션은 `review/key_results.json` 의 모든 수치를 JSON 으로 보여줍니다.\n\n"
                        f"{render_kr(kr)}"))

    # §9 KOSIS reference
    kosis_ref = read(ROOT / "data/reference/kosis_reference.json")
    parts.append(section("§9. KOSIS / 통계청 reference 통계",
                        f"본 리포가 사용한 외부 reference 분포 + 출처 + caveat. 한국 도메인 전문가가 검증할 핵심 입력.\n\n"
                        f"```json\n{kosis_ref}\n```"))

    # §10 limitations
    parts.append(section("§10. 한계 / 자기 진술 / 의심 가능 지점",
                        f"""
본 리포가 스스로 인정한 한계 (CLAIMS_LEDGER 의 C27~C35 항목 참조):

1. **모집단 차이**: KOSIS reference 가 모집단 정의가 다를 수 있음 (15+ 또는 25+). marital/education 에서 caveat 명시. housing 은 본 분석이 per-person reference 자체 추정 (±2pp 오차 가능).
2. **PC conditioning depth**: |Z| ≤ 2 까지만. |Z| ≥ 3 에서 mediation 가능성 미검증.
3. **CMI 임계 ε = 0.005 nats**: 임의 선택이나 §2.7 sensitivity 분석으로 의존성 정량화 — 핵심 결론은 ε-stable. ★★★ 검증 완료.
4. **High-cardinality bias**: §2.5 permutation null 결과, 23 direct edges 중 11개 (모두 occupation/district 포함) 가 ratio < 2 로 bias-suspect.
5. **Bootstrap CI 산출 완료**: 모든 페어 SE 매우 작음 (district~province SE=0.004 nats). 추정치 자체는 정밀.
6. **합성-내 예측가능성 검사 단일 모델 한계**: HistGradientBoostingClassifier · seed=42 사용. 다른 모델 (RF, LightGBM, NN) 에서의 robustness 미확인 (ROADMAP P8 예정). 단 leakage check (§1.4) + 5-fold CV 로 단일 split 한계는 점검 완료 — 결론 변화 없음.
7. **방향성 미해결**: 추론된 skeleton 은 무방향. DAG 화 (방향 있는 PGM) 는 시간 순서 등 추가 가정 필요.
8. **외부 검증 부분만 완료**: §2.6 KOSIS cross-tab 비교는 보도자료 인용 cell 위주. 완전 외부 검증은 KOSIS Open API 통한 P7 v2 예정.
9. **시계열 부재**: 정적 스냅샷. 생애주기·이주·세대간 이동 분석 불가.
10. **Phase 4 미진행**: 7개 자유서술 페르소나 텍스트 분석 (어휘 다양성, 고정관념) 은 미수행.

리뷰어가 특히 봐 주실 점:
- C19 (housing decoupling, info_added = -0.008 nats) 의 통계적 신뢰도 — leakage check 후에도 동일 (C30b)
- C21 (현역 인력 분해 vs 한국군 실제 구성) 의 도메인 해석 정당성
- C12, C13 (sex×field, sex×military) 한국 reference 정밀 검증
- C31 (permutation null bias correction) — 23 direct edges 중 12개만 견고 결론의 견고성
- C8 (housing per-person reference 자체 추정) 의 ±2pp 오차 가정
- METHODOLOGY §7 의 8개 임의 선택의 sensitivity
"""))

    out_path = REVIEW / "REVIEW_PACKET.md"
    out_path.write_text("".join(parts), encoding="utf-8")
    n_chars = len(out_path.read_text())
    n_lines = len(out_path.read_text().split("\n"))
    print(f"Wrote {out_path}")
    print(f"  size: {n_chars:,} chars, {n_lines:,} lines")
    print(f"  approx tokens: {n_chars // 4:,} (rough heuristic)")


if __name__ == "__main__":
    main()
