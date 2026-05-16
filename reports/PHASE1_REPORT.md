# Phase 1 — Marginal (단변량) 충실도 리포트

> **한 문단 요약**: 변수 하나씩 떼어 본 분포는 KOSIS 와 잘 맞는다. 시도/시군구 인구
> 분포는 사실상 완벽 (TVD = 0.005), 성별·학력·결혼 모두 양호 (TVD ≤ 0.05).
> housing_type 은 약한 격차 (TVD ≈ 0.08, 단독주택 -8pp 잔존; per-person reference
> 자체 추정 ±2pp 오차 고려 시 단언적 결론 어려움 — §3-4 참조).
> N = 1,000,000 이라 χ² p-value 는 모두 0 — 효과크기 (TVD) 위주로 봐야 함.

NVIDIA `Nemotron-Personas-Korea` (1,000,000 행, 26 변수, 2026-04-20 공개) 의
**개별 변수 분포가 한국 공식 통계와 얼마나 일치하는가** 를 측정한다.

> ⚠️ Phase 1은 변수 **하나씩** 만 본다. PGM이 가정한 conditional independence
> (성·학력·전공×직업 등의 결합)가 깨지는지는 Phase 2의 영역.

---

## 1. 데이터셋 요약 (실측)

| 항목 | 값 |
|---|---:|
| 총 행 수 | **1,000,000** |
| 성별 | 여자 50.44% / 남자 49.56% |
| 연령 | 19–99세, 평균 50.66, 중앙 51, 표준편차 17.6 |
| 시도 | 17개 모두 등장 |
| 시군구 | 252개 모두 등장 |
| 직업 | 2,120 개 unique 문자열 (무직 36.7% 포함) |
| 학력 | 7개 카테고리 (무학~대학원) |
| 전공 | 11개 카테고리 (해당없음 67.4%) |
| 가구유형 | 39개 |
| 주택유형 | 6개 |
| 혼인 | 4개 (배우자있음 59.3% / 미혼 25.7% / 사별 8.8% / 이혼 6.3%) |
| 병역 | 비현역 99.5% / 현역 0.5% |
| 국가 | 대한민국 100% |

전체 산출물: [`data/processed/marginals/`](../data/processed/marginals)

---

## 2. KOSIS 비교 결과 — Headline

| 변수 | 비교 reference | TVD | L∞ | 평가 |
|---|---|---:|---:|---|
| **sex** | 통계청 추계인구 19+, 2024 | **0.0006** | 0.0006 | ★★★ 사실상 완벽 |
| **province** | 행안부 주민등록 2024.12 | **0.0055** | 0.0024 | ★★★ 17개 시도 ±0.24pp 이내 |
| **education_level** | 인구주택총조사 25+ , 2020 | **0.044** | 0.024 | ★★ 모든 셀 격차 부호가 19+ vs 25+ 모집단 차이로 예상되는 방향과 일치 |
| **marital_status** | 인구주택총조사 15+, 2020 | **0.054** | 0.054 | ★★ 모든 셀 격차 부호가 19+ vs 15+ 모집단 차이로 예상되는 방향과 일치 |
| **housing_type** | 자체 추정 per-person ref (KOSIS 2023 기반), §3-4 | **0.084** | 0.080 | ★ 약한 격차 (단독주택 -8pp 잔존, reference 추정 오차 ±2pp 고려 시 확정 어려움) |

> **N=1,000,000** 이므로 χ² 검정의 p-value는 모든 변수에서 사실상 0이다.
> Phase 1에서는 TVD / L∞ 같은 효과크기(effect size) 가 더 정보적이다.
> (TVD ≤ 0.01 이면 사실상 동일, ≤ 0.05 양호, ≥ 0.10 면 모형 점검 필요)

상세 표 + 그림: [`reports/tables/kosis_comparison.md`](tables/kosis_comparison.md)

---

## 3. 변수별 해석

### 3-1. sex · province (★★★)
PGM이 **시도별 성별 인구 분포를 정확하게 재현**한다.
17개 시도 중 가장 큰 오차도 서울 +0.24pp, 세종 −0.09pp 정도.
여기까지는 NVIDIA의 marginal 통제가 제대로 작동했다고 볼 수 있다.

### 3-2. education_level (★★)
학력 7개 카테고리에서 모두 ±2.5pp 이내.
단, **공식 reference(25세+)** 와 **합성 데이터(19세+)** 의 모집단 차이로
대학·대학원이 약간 낮게 나오는 것이 자연스럽지만, **합성에서는 오히려 4년제·전문대가
+1.4 ~ +1.5pp 더 높다.** → 학력이 약간 *상향 편향*된 차이로 해석 가능.
(모집단 보정 후 재계산하면 격차는 더 클 것으로 예상)

### 3-3. marital_status (★★)
"미혼"이 reference 31.1%(15+) 대비 합성 25.7%로 −5.4pp.
이는 모집단을 19+로 좁히면 자연스럽게 좁혀진다 (15~18세는 거의 전원 미혼).
배우자있음 +3.4pp, 사별 +1.6pp 모두 19+ 보정 방향과 부호 일치.
**즉 marital_status는 "기준만 정렬하면 OK" 수준.**

### 3-4. housing_type (★) — 약한 격차

Nemotron 은 개인 단위 (1M 행 = 1M명) 이므로 per-person 거처 분포가 올바른 비교 대상. 공식 per-person 통계가 별도 발표되지 않아 본 분석이 자체 추정 — 통계청 일반가구 분포 + 1인가구 비중 35.5% + 1인가구 거처분포 + 평균 가구원수 2.21 로 가구원수 가중치 적용 (`scripts/20_housing_unit_correction.py`).

| 거처 | per-person reference (추정) | Nemotron | 격차 (pp) |
|---|---:|---:|---:|
| 아파트 | 58.6% | 62.1% | +3.5 |
| 단독주택 | 24.9% | 16.9% | −8.0 |
| 연립·다세대 | 11.0% | 14.0% | +3.0 |
| 주택 이외의 거처 | 4.0% | 6.0% | +2.0 |
| 비주거용 건물 | 1.3% | 1.0% | −0.3 |
| **TVD** | — | — | **0.084** |

단독주택 -8pp 잔존 격차가 가장 큰 셀별 차이. 다만 per-person reference 자체 추정 오차 (±2pp), 다인가구 평균 가구원수의 거처유형별 차이 (본 분석에서 단일값으로 단순화) 를 고려하면 확정적 결론 어려움.

가능한 격차 원인 가설:
- 시드 통계가 도시 가중 표본 (KOSIS 외 부동산/임대 데이터 혼합) 일 가능성
- 거처유형별 가구원수 분포의 미세 차이가 추정에 반영되지 않은 효과

→ **Phase 3 의 housing decoupling 결론은 internal structure 분석이라 본 비교와 무관, 그대로 유효.**

### 3-5. military_status (메모)
현역 비율 0.5% (5,282명). 변수 의미는 **"현역 군 인력 신분 (직업군인 + 의무복무 통합)"** 으로 미국식 'active duty' 에 가까움 — 데이터 카드에 정의가 없어 의무복무만 의미하는지 모호하나, 계급별 분해 (병사 13% / 부사관 50% / 장교 37%) 와 여성 비율 10% 가 한국군 현역 인력 구성과 부합 (Phase 2 §3-6, Phase 3 §3-4 참조). 0.5% 라는 marginal 비율도 한국군 총 인력 약 50만 / 19+ 성인 약 4400만 = 약 1.1% 와 같은 자릿수.

### 3-6. occupation (메모)
2,120 개 unique 직업명. **"무직" 36.7%** 라는 한 카테고리가 가장 큼.
이는 (i) 가정주부, (ii) 학생, (iii) 은퇴자, (iv) 실업자를 모두 합친 것으로 보이며,
**Phase 2 / 3에서 무직과 marital, age, education의 결합을 봐야 의미 해석 가능**.

---

## 4. 공식 데이터카드 주장과의 정합

NVIDIA 데이터 카드 핵심 주장 → 본 검증 결과:

| 주장 | 검증 |
|---|---|
| "한국 인구통계와 지리·사회 특성 분포 반영" | ✅ 시도/성/연령에서 사실 |
| "PGM으로 인구 분포 통제" | ✅ marginal level에서는 통제 작동 |
| "세부 직업 배정 시 성·소득·학력·전공 *독립* 가정" | Phase 1에서는 평가 불가 → Phase 2 필요 |
| "검증·평가는 NeMo Data Designer 내장" | 외부 재현 가능한 marginal 검증 결과 본 리포가 첫 사례 |

---

## 5. Phase 1 결론

- **단변량(marginal) 수준에서는 sex / province / 학력 / 혼인 모두 잘 재현**된다.
  특히 시도 17개의 비중은 ±0.24pp 이내로 매우 정확하다.
- **약한 격차: housing_type 단독주택** — per-person reference 대비 -8pp 잔존 (TVD ≈ 0.08). 단 reference 자체 추정 오차 ±2pp 고려 시 확정적 결론 어려움.
- **N=1M 이라 chi-square의 p-value는 의미가 없다.** TVD/L∞ 같은 효과크기 위주로 봐야 한다.
- **단변량이 맞다고 결합 분포가 맞는 것은 아니다.** 다음 단계(Phase 2)는
  province×housing, sex×bachelors_field, age×education, age×marital 같은 2차 분포에서
  PGM의 독립성 가정이 어느 정도 깨지는지를 측정한다.

---

## 6. 재현 방법

```bash
git clone <this repo>
cd nemotron-personas-korea-audit
uv venv .venv && source .venv/bin/activate
uv pip install -r requirements.txt
python scripts/01_download.py     # 약 2GB
python scripts/02_marginals.py
python scripts/03_compare_kosis.py
```

산출물:
- `data/processed/marginals/*.csv` — 변수별 분포
- `data/processed/marginals_summary.json` — 요약
- `data/processed/kosis_comparison.json` — KOSIS 비교 metrics
- `reports/tables/kosis_comparison.md` — 비교표
- `reports/figures/marginal_*.png`, `compare_*.png` — 그림

## 7. 한계 (Phase 1 자체의)

- **모집단 차이로 reference 표준화 일부 자체 추정**: marital (15+), education (25+) 은 19+ 보정을 못 한 채 원본 비교. housing 은 본 분석이 per-person reference 를 자체 추정 (1인가구 비중·평균 가구원수 가중치 적용, ±2pp 오차 가능). 더 정밀한 비교는 KOSIS 원시 표·마이크로데이터 직접 접근 필요.
- 모든 변수가 KOSIS와 직접 매칭되지 않음 (occupation 은 KSCO 7차 분류 매핑 필요 — [ROADMAP P5](../ROADMAP.md); family_type 은 통계청 가구 분류와 상이).
- 페르소나 텍스트 7종은 본 phase 에서 다루지 않음 ([ROADMAP P9: Phase 4](../ROADMAP.md)).
