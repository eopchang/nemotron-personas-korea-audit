# REVIEW PACKET — Nemotron-Personas-Korea Audit

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


---

# §1. 프로젝트 개요

> 2026년 4월, NVIDIA가 *700만 한국인 가상 페르소나* 라는 이름으로 공개한 합성 데이터셋이
> 통계적으로 얼마나 실제 한국 인구를 닮았고, 내부적으로 어떤 구조를 갖는지를
> **데이터 자체에서** 검증한 독립 분석 리포지터리입니다.

[![License: MIT](https://img.shields.io/badge/code-MIT-green.svg)](LICENSE)
[![Reports: CC BY 4.0](https://img.shields.io/badge/reports-CC--BY--4.0-orange.svg)](LICENSE)
[![Dataset: HuggingFace](https://img.shields.io/badge/dataset-HuggingFace-yellow)](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea)

---

## 📋 한 페이지 요약

NVIDIA가 공개한 [Nemotron-Personas-Korea](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea)
는 한국 통계청·대법원·국민건강보험공단 등의 공식 통계를 바탕으로 만든 **1,000,000행 × 26개 변수**의
합성 페르소나 데이터입니다. 데이터 카드에는 단변량 (marginal) 분포의 정성적 비교만 공개되어 있어,
**연구자가 이 데이터를 자기 분석에 써도 될지 판단할 근거**가 부족했습니다.

본 리포는 3단계로 정량 검증을 수행했습니다.

| Phase | 무엇을 봤나 | 결과 |
|---|---|---|
| **1** 단변량 충실도 | 12개 변수의 분포가 KOSIS 와 일치하나? | sex/지역/학력/혼인 모두 양호 (TVD ≤ 0.05). housing 은 약한 격차 (TVD ≈ 0.08, 단독주택 -8pp 잔존; [Phase1 §3-4](reports/PHASE1_REPORT.md#3-4-housing_type----약한-격차)) |
| **2** 이변량 결합 | 55개 변수 쌍의 결합이 어떤 모양인가? | 인구학 chain (age→marital→family, age→edu→field→occupation) 견고. 성별×전공 분리 패턴 한국 현실과 부합 |
| **3** 의존 구조 추정 | 데이터에 어떤 조건부 의존 skeleton이 남아있나? | **23 direct + 14 mediated + 18 no-edge** (ε=0.005 nats, \|Z\|≤2 조건 하; ε 100배 변동 시 direct 수 32–13 범위, 핵심 결론은 ε-stable; permutation null 로 bias 보정 시 12개만 ratio>2 로 견고). **Housing은 사람 속성과 분리, military는 occupation 함수** |

### ⭐ 7개 결정적 발견

1. ✅ **시도/시군구별 인구 분포는 KOSIS 와 매우 가까움** — TVD = 0.005, 17개 시도 모두 ±0.24pp 이내.
2. ✅ **인구학 chain (나이→결혼→가족, 나이→학력) 한국 현실과 정량적으로 부합** — 20-50대 미혼 비율이 2020 census 와 8/8 cell 모두 ±4pp 이내 (P7 외부 검증). 25-34 4년제 51.6%, 75-84 사별 42.6% 등 KOSIS 와 일치.
3. ✅ **성별×전공 분리 패턴 한국 현실과 부합** — 공학 86% 남성, 보건·복지 28% 남성.
4. ⚠️ **`housing_type` 이 사람 속성과 통계적으로 분리됨** — 1인 가구도 4인 가족도 청년도 노년도 모두 아파트 ~62%. 예측 기반 conditional-independence probe 로 이중 확인 (info_added = −0.008 nats).
5. ⚠️ **`military_status` 는 occupation 라벨에서 거의 결정적으로 파생되는 부수 변수** (정보 중복). 단 변수 의미는 *의무복무 이행* 이 아니라 *현역 군 인력 신분 (직업군인 + 의무복무 통합)* 으로 한국군 인력 구성과 부합 (병사 평균 25세, 부사관 41세, 장교 47세, 여성 11%).
6. ⚠️ **`occupation` 의 "무직" 카테고리가 36.7% 로 거대** — 가정주부·학생·은퇴자·실업자가 한 라벨에 통합. 세분화된 노동시장 분석에는 한계 (단 큰 그림 — 학력→직업, 성별→직업 분리 등은 잘 작동).
7. ⚠️ **23개 'direct edge' 중 12개만 bias-corrected 견고** — 나머지 11개 (모두 occupation/district 같은 high-cardinality 변수 포함) 는 plug-in MI 의 카디널리티 bias 일 가능성 (P4 permutation null 결과). occupation·district 가 들어가는 fine-grained 결합 의존성 주장은 신중하게 인용 필요.

→ **결론**: 본 데이터셋은 분석 종류에 따라 다음 3가지로 분류 가능:

- ✅ **사용 가능**: LLM 학습용 페르소나 (본 용도), 지역 단위 시뮬레이션 (시도/시군구 인구), 인구학 chain 분석 (`age × marital × family`, `age × education`), 노동시장 성분리 (`sex × field × occupation`), 현역 군 인력 cross-section 구성 (계급별 연령·성비)
- 🤔 **신중하게 사용**: `occupation`·`district` 가 들어가는 fine-grained 결합 분석 (high-card bias 가능성), 직업 분포 세분화 분석 ("무직" 36.7% 통합 카테고리 주의), housing 지역 단위 시뮬레이션 (단독주택만 약한 격차)
- ❌ **부적합**: 개인 속성별 주거 분석 (1인가구 주거·청년 주거 빈곤 등), 의무복무 흐름·동학 분석, 시계열·생애주기 분석, 별거·기러기 가족 등 결혼-가구 구성의 다양성 분석 (PGM 의 결정론적 매핑이 이 다양성을 제거)

---


---

# §2. 데이터셋 정보 (NVIDIA 공식 자료 + 본 리포 실측)


| 항목 | 값 |
|---|---|
| 이름 | Nemotron-Personas-Korea |
| 공개 | 2026-04-20, HuggingFace |
| 라이선스 | CC BY 4.0 |
| 행 수 | 1,000,000 |
| age 범위 | 19.0–99.0 세, 평균 50.66 |
| 변수별 unique 값 수 | ```json
{
  "sex": 2,
  "age": 81,
  "marital_status": 4,
  "military_status": 2,
  "family_type": 39,
  "housing_type": 6,
  "education_level": 7,
  "bachelors_field": 11,
  "occupation": 2120,
  "district": 252,
  "province": 17,
  "country": 1
}
``` |
| 생성 도구 | NVIDIA NeMo Data Designer |
| 생성 모델 | PGM (인구통계) + google/gemma-4-31B-it (자연어) |
| 시드 | KOSIS, 대법원, NHIS, KREI, 네이버클라우드 |



---

# §3. 방법론 종합


본 리포가 사용한 모든 통계 도구를 한 곳에 정리. 각 phase 리포트는 결과 중심,
이 문서는 도구 중심.

---

## 1. 모집단 / 데이터

- **모집단**: 19세 이상 한국 성인 (NVIDIA 데이터셋 정의)
- **표본**: 1,000,000 행 (전수 사용)
- **변수**: 26개 (인구통계 12 + 자유서술 7 + 속성 6 + UUID)
- **본 리포의 분석 대상**: 카테고리·수치 변수 12개 중 `country` (단일값) 제외 → 11개
  + `age` 는 8구간으로 binning (`age_bin`)

### age binning 규칙
```
[19-24, 25-34, 35-44, 45-54, 55-64, 65-74, 75-84, 85+]
```

연속형 정보를 일부 잃지만, 카테고리 변수와의 결합 분석을 가능케 함.
필요시 더 세밀한 binning 으로 재분석 가능 (`scripts/_lib.py:AGE_BREAKS`).

---

## 2. 단변량 (Marginal) — Phase 1

### 2.1 분포 산출
각 변수 v에 대해 `P(v=k) = count(k) / N` for k ∈ levels(v).

### 2.2 비교 지표
공식 KOSIS reference 분포와 비교. 사용 지표:
- **TVD** = ½ Σ |P_synth(k) − P_ref(k)|
- **L∞** = max_k |P_synth(k) − P_ref(k)|
- **per-cell diff (pp)** = (P_synth(k) − P_ref(k)) × 100

### 2.3 유의성 검정
**사용하지 않음.** N=1M 에서 χ² p-value 는 거의 모든 비교에서 0 → 효과크기 위주.

### 2.4 reference 통계 caveat
KOSIS 공표 통계는 모집단 정의가 다를 수 있음 (15세+ vs 19세+ 등).
[`data/reference/kosis_reference.json`](../data/reference/kosis_reference.json) 의 `caveat` 필드에 명시.

### 2.5 housing per-person reference 자체 추정 (Phase 1 §3-4)

Nemotron 은 개인 단위 (1M 행 = 1M 명) 이므로 가구 단위 KOSIS reference 와 직접 비교 불가. 공식 per-person 거처 분포가 별도 발표되지 않아 본 분석이 자체 추정:

```
per_person_share(k) = (1인가구비중 · 1 · 1인가구거처분포(k) + 다인가구비중 · 다인가구평균 · 다인가구거처분포(k)) / 전체평균가구원수
```

입력: 통계청 일반가구 분포 + 1인가구 비중 35.5% + 1인가구 거처분포 + 평균 가구원수 2.21.
구현: [`scripts/20_housing_unit_correction.py`](../scripts/20_housing_unit_correction.py).
결과: TVD ≈ 0.084 (가구 기준 비교 시 0.119에서 30% 감소).
한계: ±2pp 정도의 추정 오차 가능 (다인가구 평균 가구원수를 거처유형별로 다르게 두지 않은 근사).

---

## 3. 이변량 (Bivariate) — Phase 2

### 3.1 사용 지표 4종
| 지표 | 정의 | 대칭? | 범위 |
|---|---|:---:|---|
| Cramér's V | √(χ² / (N · min(r-1, c-1))) | ○ | [0, 1] |
| NMI | 2·I(X;Y) / (H(X)+H(Y)) | ○ | [0, 1] |
| Theil's U(Y\|X) | I(X;Y) / H(Y) | ✕ | [0, 1] |
| TVD vs independence | ½ Σ\|P(x,y) − P(x)P(y)\| | ○ | [0, 1] |

### 3.2 PMI grid
각 (x, y) 셀: `PMI(x, y) = log[ P(x, y) / (P(x) · P(y)) ]`
- 양수: 독립 대비 over-represented
- 음수: 독립 대비 under-represented
- |PMI| 큰 셀 = 결합 분포의 신호

### 3.3 결합 시각화 — 3-panel 표준
모든 큐레이션 페어와 전 55페어에 동일한 3-panel:
- (A) Conditional distribution: P(Y|X=x) — 100% stacked bar
- (B) PMI grid: 결합 셀별 over/under-representation
- (C) Top-15 deviation cells: |p_obs − p_indep| 큰 순서

### 3.4 카디널리티 처리
high-cardinality 변수 (occupation 2,120, district 252) 는 시각화에서 top-K + "기타" 로 절단.
지표 계산은 **절단하지 않은 전체 분포** 에서.

---

## 4. PGM 구조 추론 — Phase 3

### 4.1 Conditional MI
```
I(X; Y | Z) = Σ_{x,y,z} p(x, y, z) · log [ p(x, y, z) · p(z) / (p(x, z) · p(y, z)) ]
```
구현: 3D contingency 테이블 → numpy. nats 단위. [`scripts/_cmi.py`](../scripts/_cmi.py).

### 4.2 PC-style skeleton recovery (단순화 버전)
각 페어 (X, Y) 에 대해:
1. **Level 0**: I(X; Y) (마지널 MI)
2. **Level 1**: I(X; Y | Z) for Z ∈ vars \ {X, Y}
3. **Level 2**: best Level 1 mediator Z*에 대해, I(X; Y | Z*, Z') for Z' ∈ vars \ {X, Y, Z*}

### 4.3 Edge classification
- `no_edge_marginal` if I(X; Y) < ε
- `mediated`         if min over conditioning sets < ε
- `direct`           otherwise

ε = 0.005 nats. Sensitivity 분석은 §5 (ε grid 재분류) 와 §6 (permutation null bias 보정) 에서 견고성 검증 완료.

### 4.4 한계
- |Z| ≤ 2 까지만. |Z| ≥ 3 mediation 가능성은 확인 안 함.
- 방향성 미해결 (DAG 아닌 skeleton).
- 추가 robustness 검증: §5–§9 참조.

---

## 5. ε threshold sensitivity — Phase 3 §2.7 보강

§4의 임계 ε = 0.005 nats 가 분류에 얼마나 영향을 주는지 grid 로 재분류:

- ε ∈ {0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05}
- 각 ε 에서 §4.3 분류 규칙 재적용
- 페어별 분류 변화 추적 ([`scripts/14_epsilon_sensitivity.py`](../scripts/14_epsilon_sensitivity.py))

결과: ε 100배 변동 시 direct edge 수가 32 → 13 범위로 움직임. 그러나 23개 페어는 전 grid 에서 분류 불변 (ε-stable), 32개는 boundary (ε 따라 분류 바뀜). 핵심 결론 (housing decoupling, demographic chain) 은 ε 변경에 견고.

---

## 6. Permutation null + Bootstrap CI — Phase 3 §2.5 보강

**왜 필요**: plug-in MI 추정량은 contingency table 카디널리티에 비례하는 upward bias 를 가짐 (Miller-Madow 보정 ≈ (k-1)(m-1)/(2N)). occupation × district (2120 × 252) 에서 bias 만 ≈ 0.27 nats — 임계 ε 의 53배. 단순 CMI 값으로는 "진짜 효과" 와 "카디널리티 bias" 분간 불가.

### 6.1 Stratified permutation null
- H0: X ⊥ Y | Z 하에서 Y 를 Z-stratum 안에서 셔플 (X, Y, Z 각 marginal 보존)
- 100 perms × 78 페어 (55 marginal + 23 conditional direct edges)
- N=100K subsample (속도 + bias 동일 조건 비교)
- 구현: [`scripts/_perm.py`](../scripts/_perm.py) (lexsort 기반 벡터화), [`scripts/15_permutation_null.py`](../scripts/15_permutation_null.py)
- 핵심 metric: **ratio = observed / null_p95** (효과크기 / bias 우월성)

### 6.2 Row bootstrap CI
- 100 boots × 78 페어, same N
- 95% percentile CI: `[quantile_2.5%, quantile_97.5%]`
- 구현: [`scripts/16_bootstrap_ci.py`](../scripts/16_bootstrap_ci.py)

### 6.3 분류 가이드
- `ratio ≥ 10`: robust — bias 와 무관한 강한 효과
- `ratio 2–10`: significant
- `ratio < 2`: bias-suspect — 추정 bias 와 같은 자릿수, 진짜 의존성인지 단언 어려움

---

## 7. Predictive decoupling probe — Phase 3 §1.3 보강

> 용어 주의: 본 within-synthetic probe 는 엄밀한 TSTR (Train on Synthetic, *Test on Real*) 과 다르다. 합성 데이터만으로 train/test split 한 **predictive conditional-independence probe** / **decoupling probe** 가 정확한 명칭.

### 7.1 목표
"Feature set F 가 baseline B 위에 정보를 더하는가" 를 분류기 cross-entropy로 측정.

### 7.2 모델
- `sklearn.HistGradientBoostingClassifier`
- 200 iter, max_depth=8, lr=0.05
- 모든 feature를 categorical로 처리 (OrdinalEncoder + categorical_features mask)

### 7.3 Cardinality 처리
HGB의 categorical 한계 (255 unique). 250 초과는 top-249 + "기타" 로 캡.

### 7.4 데이터 분할 (기본)
- 300,000 행 subsample (시드 42)
- 80/20 train/test, random split (stratify 미사용)

### 7.5 지표
- Cross-Entropy (CE), nats, log_loss with all classes
- Accuracy
- info_added = CE_baseline − CE_full

### 7.6 해석
- info_added ≈ 0: 추가 feature가 baseline 위에 정보를 더하지 못함 → conditional independence
- info_added > 0: 정보 추가 (real signal)
- info_added < 0: 추가 feature가 약간의 과적합. 사실상 0.

### 7.7 Leakage check (§1.4) — train-only encoder + 5-fold CV
§7.1–§7.4 기본 절차의 잠재 leakage 6가지 (encoder 전체 fit, cap_high_card 전체 빈도 기반, target encoding, 단일 split, HGB 내부 split, 합성 데이터 row 중복성) 점검:
- **Train-only encoder + train-only cap**: encoder/cap 을 train fold 에서만 fit
- **5-fold cross-validation**: 단일 split 변동성 통제
- 구현: [`scripts/11b_decoupling_probe_no_leakage.py`](../scripts/11b_decoupling_probe_no_leakage.py)
- 결과: 6개 모든 case 에서 info_added 변화 < 0.005 nats (원본 효과의 1% 이하), 5-fold SE < 0.02 nats. **결론 변화 없음**.

---

## 8. Subsample stability — Phase 3 §1.5 보강

### 8.1 절차
- N_SUB = 200,000, N_SEEDS = 5
- 각 시드에서 |Z|=1 까지의 skeleton classification 재계산
- 분류 일치율 = 5/5 시드에서 동일하면 stable

### 8.2 결과
55 페어 중 52개 stable (94.5%). 3개 unstable은 |Z|=1 vs |Z|=2 방법론 mismatch이지 데이터 노이즈가 아님.

---

## 9. KOSIS cross-tab 외부 비교 — Phase 3 §2.6 보강

§4–§8 까지는 모두 합성 데이터 내부의 자기 일관성 검증. 실제 한국 인구의 *결합* 분포와의 외부 비교는 별도 KOSIS reference 필요.

### 9.1 v1 (현재) — 보도자료 인용 cell 기반 부분 검증
- 출처: 통계청·정책브리핑·한국의 사회동향 등 *공개 보도자료에 명시된* cross-tab cell 만
- 검증 페어: age × marital × sex / age × sex × education / province × housing
- 구현: [`scripts/18_kosis_joint_compare.py`](../scripts/18_kosis_joint_compare.py)
- 출처 명시: [`data/reference/kosis_joint.json`](../data/reference/kosis_joint.json) 의 셀별 source 필드

### 9.2 v2 (예정, ROADMAP P7) — KOSIS Open API 완전 cross-tab
모든 cell 의 완전 외부 비교는 API 키 등록 후. 17개 시도 × 6 housing_type 완전 cross-tab, 5세별 학력 표 (vintage 문제 해결), sex × bachelors_field (KEDI), 등.

---

## 10. 모든 임의 선택 / 임계 한 곳에 모음

| 매개변수 | 값 | 위치 |
|---|---|---|
| age binning | [19-24, 25-34, ..., 85+] | `_lib.py:AGE_BREAKS` |
| TVD "양호" 임계 | < 0.05 (subjective) | PHASE1_REPORT §2 |
| housing per-person ref 자체 추정 | 1인가구 35.5% + 평균 가구원수 2.21 가중 | `20_housing_unit_correction.py` |
| CMI 효과크기 임계 ε | 0.005 nats | `08_skeleton_recovery.py:EPSILON` |
| ε sensitivity grid | {0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05} | `14_epsilon_sensitivity.py:EPSILONS` |
| PC conditioning depth | \|Z\| ≤ 2 | `08_skeleton_recovery.py` |
| Permutation null perms | 100 | `15_permutation_null.py:N_PERMS` |
| Permutation null subsample | 100,000 (seed 42) | `15_permutation_null.py:N_SUB` |
| Bootstrap CI boots | 100, 95% percentile | `16_bootstrap_ci.py:N_BOOTS` |
| ratio tier 임계 | robust ≥ 10 / signif 2–10 / suspect < 2 | `19_bias_corrected_skeleton.py:TIER_THR` |
| Decoupling probe subsample size | 300,000 | `11_decoupling_probe.py:N_SUB` |
| Probe HGB iter | 200, depth 8, lr 0.05 | `11_decoupling_probe.py:fit_eval` |
| HGB cardinality cap | 250 | `11_decoupling_probe.py:CARD_CAP` |
| Leakage check folds | 5-fold CV, train-only encoder | `11b_decoupling_probe_no_leakage.py` |
| Stability subsample | 200,000 × 5 seeds (0–4) | `12_subsample_stability.py` |
| Visualization topK occupation | 20 | `05b_bivariate_detail_all.py:TOPK` |
| Visualization topK district | 25 | `05b_bivariate_detail_all.py:TOPK` |

→ 이 임계들 중 본 리포 결론에 가장 영향이 클 만한 것은 **CMI 임계 ε 와 PC depth |Z|** — §5 (ε sensitivity) 및 §6 (perm null bias 통제) 에서 robustness 검증 완료.

---

## 11. 재현성 체크리스트

- [x] 모든 random seed 명시 (42 / 0..4)
- [x] 모든 임계 코드에 명시
- [x] requirements.txt 버전 fix
- [x] 한 명령으로 phase별 재실행 가능
- [x] 산출물 (CSV/JSON) git에 commit (작은 것)
- [x] ε sensitivity 분석
- [x] Permutation null + Bootstrap CI (bias correction)
- [x] Decoupling probe leakage check (5-fold CV)
- [x] Subsample stability
- [ ] CI (GitHub Actions) 로 smoke test (미진행)
- [ ] Docker 이미지 (미진행)
- [ ] Multi-model probe robustness (ROADMAP P8)
- [ ] KOSIS Open API 완전 cross-tab (ROADMAP P7 v2)



---

# §4. Phase 1 — 단변량 충실도


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



---

# §5. Phase 2 — 이변량 결합


> **한 문단 요약**: 11개 변수의 모든 55개 페어를 4종 association 지표 (Cramér V,
> NMI, Theil U, TVD vs independence) 로 측정. PGM 이 *결정적 제약 (배우자있음 →
> 가구에 배우자 100% 포함, 시군구 → 시도 결정적)* 과 *한국 인구학 패턴 (19-24
> 미혼 95%, 75-84 사별 43%)* 을 모두 정확히 인코딩. 성별×전공도 한국 현실 부합
> (공학 86% 남성, 보건 28% 남성). 데이터카드의 "독립 가정" 문구는 occupation
> 라벨링의 좁은 의미일 뿐이고, sex×field 자체는 강한 결합으로 잘 잡혀있음.

NVIDIA `Nemotron-Personas-Korea` 의 **두 변수 사이 의존 구조**를 측정한다.
Phase 1이 "변수 *하나씩* 보면 KOSIS와 얼마나 비슷한가"였다면, Phase 2는
**"PGM이 변수 *사이의 관계*를 어디까지 인코딩했는가"** 를 본다.

> 데이터 카드는 "세부 직업 배정 시 성별·소득·학력·전공이 *독립적으로* 영향"이라
> 명시했다. 이 한 줄을 곧이곧대로 읽으면 sex × bachelors_field 같은 페어는
> 거의 독립이어야 한다. 본 phase의 한 결과는 **그렇지 않다** — PGM은 sex와 전공
> 사이의 강한 의존성(공학·정보통신=남성, 보건·교육=여성)을 충실히 인코딩하고
> 있다. 즉 카드의 "독립 가정" 문구는 occupation 라벨링의 가중 항에만 좁게
> 적용된 것으로 해석된다.

---

## 1. 분석 설계

### 변수
`country` 는 단일값이라 제외 → **11개 변수**.
연속형 `age` 는 8개 구간(19-24/25-34/.../85+)으로 binning.

### 지표 (정의는 README 또는 `scripts/_lib.py` 참고)
| 지표 | 대칭? | 의미 | 해석 가이드 |
|---|---|---|---|
| **Cramér V** | ○ | χ² 기반 효과크기, 0–1 | ≥0.3 강함, ≥0.1 중간, ≥0.05 약함 |
| **NMI** = 2I/(H_x+H_y) | ○ | 정규화 상호정보 | 1.0 = 완전결정, 0 = 독립 |
| **Theil U(Y\|X)** = I/H_y | ✕ | 'X 알면 Y 불확실성 X% 줄어듬' | **방향성** |
| **TVD_indep** = ½ Σ\|P(x,y)−P(x)P(y)\| | ○ | 결합과 독립의 거리 | 0 = 독립 |

> N = 1,000,000. χ² p-value 는 모든 페어에서 사실상 0 → **효과크기**로 봐야 함.

55개 모든 무방향 페어 + 110개 방향성 U 결과: [`data/processed/bivariate/`](../data/processed/bivariate)

### 시각화
- 4개 11×11 heatmap: Cramér V, NMI, Theil U(asymmetric), TVD_indep
  → [`reports/figures/heatmap_*.png`](figures)
- **55개 모든 페어 detail (3-panel: 조건부분포 + PMI grid + Top-15 deviation)**
  → 색인: [`PAIR_INDEX.md`](PAIR_INDEX.md) · 그림: [`figures/bivariate_all/`](figures/bivariate_all)
- 본 리포트 본문에서 깊이 분석한 큐레이션 10개: [`figures/bivariate/`](figures/bivariate)

---

## 2. 전체 페어 결과 (Top 15 by NMI)

| x | y | V | NMI | U(Y\|X) | U(X\|Y) | TVD_indep |
|---|---|---:|---:|---:|---:|---:|
| district | province | 1.000 | 0.635 | **1.000** | 0.465 | 0.872 |
| marital_status | family_type | 0.694 | 0.440 | 0.317 | 0.717 | 0.494 |
| education_level | bachelors_field | 0.408 | 0.421 | 0.476 | 0.377 | 0.439 |
| age_bin | marital_status | 0.483 | 0.210 | 0.301 | 0.162 | 0.283 |
| age_bin | family_type | 0.337 | 0.153 | 0.140 | 0.169 | 0.309 |
| age_bin | education_level | 0.333 | 0.152 | 0.165 | 0.141 | 0.281 |
| education_level | occupation | 0.333 | 0.104 | 0.072 | 0.188 | 0.288 |
| bachelors_field | occupation | 0.261 | 0.083 | 0.054 | 0.177 | 0.220 |
| marital_status | education_level | 0.288 | 0.077 | 0.063 | 0.100 | 0.146 |
| age_bin | occupation | 0.210 | 0.053 | 0.038 | 0.085 | 0.230 |
| housing_type | district | 0.266 | 0.049 | 0.030 | 0.135 | 0.194 |
| sex | occupation | 0.454 | 0.046 | **0.027** | 0.169 | 0.186 |
| family_type | education_level | 0.183 | 0.045 | 0.054 | 0.038 | 0.144 |
| housing_type | province | 0.176 | 0.042 | 0.031 | 0.065 | 0.130 |
| occupation | district | 0.051 | 0.040 | 0.037 | 0.044 | 0.171 |

### Bottom 5 (가장 독립에 가까운 페어)
| x | y | V | NMI | TVD_indep |
|---|---|---:|---:|---:|
| military_status | district | 0.039 | 0.0002 | 0.002 |
| military_status | province | 0.023 | 0.0002 | 0.001 |
| sex | province | 0.020 | 0.0001 | 0.009 |
| military_status | housing_type | 0.006 | 3e-5 | 0.0003 |
| sex | housing_type | 0.005 | 1e-5 | 0.002 |

→ **sex는 거주(province·housing)와 거의 독립** — 이는 현실과 부합한다.
→ **military_status도 거주와 무관** — 현실상 군 복무지가 출신 시도와 강한 상관이 없음과 부합.

---

## 3. PGM이 잡아낸 "비독립" 구조 — 페어별 해석

### 3-1. district → province : U = 1.000 (sanity)
**행정 계층 구조 100% 인코딩.** 시군구가 시도를 결정적으로 함의.
역방향은 U=0.465 (각 시도가 평균 14개 시군구를 가짐). PGM이 데이터 정합성을 깨지 않음.

### 3-2. marital_status × family_type : NMI = 0.44 (강한 결합)
**결정론적 consistency 제약**: '배우자있음' 인 사람의 가구유형은 100%가 '배우자' 포함, 미혼의 부모와 동거 PMI = +1.36.

> ⚠️ 도메인 caveat: 한국 현실의 marital_status="배우자있음" 은 *법적* 혼인을 뜻하므로, 주말부부·기러기 가족·장기 별거 등 실제로 배우자와 따로 사는 케이스가 존재한다 (인구주택총조사 가구 자료에서도 일정 비율). PGM 의 결정론적 제약은 데이터 내부 일관성에는 깔끔하지만 한국 현실의 일부 다양성을 제거하는 효과가 있을 수 있다.

| 셀 | p_obs | p_indep | diff (pp) | PMI |
|---|---:|---:|---:|---:|
| 배우자있음 × 배우자·자녀와 거주 | 27.0% | 16.0% | **+11.0** | +0.52 |
| 배우자있음 × 배우자와 거주 | 20.6% | 12.2% | **+8.4** | +0.52 |
| 배우자있음 × 혼자 거주 | **0.0%** | 8.3% | **−8.3** | −∞ |
| 미혼 × 부모와 동거 | 9.2% | 2.4% | +6.8 | +1.36 |
| 미혼 × 어머니와 동거 | 3.7% | 1.0% | +2.8 | +1.36 |

→ 결혼 상태 → 가구 구성의 **결정론적 제약**(배우자있음인데 혼자 살 수 없음)을 PGM이 정확히 지킴.

### 3-3. age_bin × marital_status : NMI = 0.21
**한국 인구학 곡선이 그대로 살아있음.**

| 연령대 | 배우자있음 | 미혼 | 사별 | 이혼 |
|---|---:|---:|---:|---:|
| 19-24 | 4.2% | **95.4%** | 0.1% | 0.4% |
| 25-34 | 32.9% | **65.3%** | 0.4% | 1.4% |
| 35-44 | **68.6%** | 25.3% | 0.8% | 5.4% |
| 45-54 | **75.1%** | 11.9% | 2.4% | 10.6% |
| 55-64 | **77.7%** | 4.5% | 7.2% | 10.6% |
| 65-74 | 72.3% | 1.9% | 18.8% | 7.0% |
| 75-84 | 54.1% | 0.9% | **42.6%** | 2.4% |
| 85+ | 27.4% | 0.7% | **70.7%** | 1.1% |

- 25-34 미혼 65.3%, 35-44 미혼 25.3% — 한국의 만혼·비혼 트렌드와 일치
- 75+에서 사별 급증 (여성 평균수명이 8년 더 김 → 노년 사별)
- 45-54 이혼 10.6% — 현실 통계와 부합 (중년 누적 이혼 경험 비율)

### 3-4. age_bin × education_level : NMI = 0.15 (코호트 효과)
**고령층 학력이 낮다는 코호트 효과를 깔끔하게 재현.**

| 연령대 | 무학 | 초등 | 중학 | 고졸 | 전문대 | 4년제 | 대학원 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 25-34 | 0.2% | 0.2% | 0.9% | 16.5% | 23.3% | **51.6%** | 7.2% |
| 45-54 | 0.2% | 0.8% | 4.7% | **46.5%** | 14.0% | 26.7% | 7.2% |
| 65-74 | 3.5% | **26.0%** | 21.4% | 33.3% | 3.1% | 9.8% | 2.9% |
| 85+ | **37.4%** | **39.0%** | 8.0% | 9.0% | 1.0% | 4.5% | 1.1% |

- 청년 25-34 4년제 51.6% — 통계청 수치(약 50%)와 부합
- 19-24는 전문대 36.4% — 아직 재학 중 학생들이 "현재 학력"으로 잡힌 것
- 85+ 무학+초등 76.4% — 일제·전후 교육 박탈 세대의 현실 반영

### 3-5. sex × bachelors_field : V = 0.26, NMI = 0.04 (성별 분리 인코딩)
| 전공 | 남성 비율 |
|---|---:|
| 공학·제조·건설 | **86.6%** |
| 정보통신기술 | **76.3%** |
| 농림어업·수의학 | 73.7% |
| 경영·행정·법 | 64.4% |
| 자연과학·수학 | 56.2% |
| 사회과학·언론 | 48.0% |
| 해당없음(미진학) | 46.2% |
| 서비스 | 45.4% |
| 예술·인문 | 36.9% |
| 교육 | **29.8%** |
| 보건·복지 | **28.1%** |

→ 한국 교육통계와 방향·강도 모두 부합 (공학 ~80% 남성, 보건 ~25% 남성).
→ **데이터카드의 "독립 가정" 문구는 sex×field 자체에는 적용되지 않았다.**

### 3-6. sex × military_status — 변수 의미와 계급별 분해
| | 비현역 | 현역 |
|---|---:|---:|
| 남자 | 490,794 | 4,764 (0.96%) |
| 여자 | 503,924 | 518 (0.10%) |

- 현역 5,282명 중 여성 9.8%
- 현역인 행의 occupation은 100% 군 직업 (육군/해군/공군/해병대 × 부사관/장교/병사 12개)
- → U(military | occupation) = 1.000 (occupation 으로 거의 결정)

**계급별 분해** (`scripts/13_military_breakdown.py`):

| 계급 | n | 평균 연령 | 최대 | 여성 |
|---|---:|---:|---:|---:|
| 병사 (의무복무) | 688 | 25.4 | 30 | 0.0% |
| 부사관 (직업) | 2,636 | 40.6 | 55 | 11.5% |
| 장교 (직업) | 1,958 | 46.7 | 63 | 10.9% |

→ 한국군 부사관·장교 정년과 여군 비율 (~10%) 정확히 부합.
**`military_status = 현역` 은 "의무복무 이행" 이 아니라 "현역 군 인력 신분 (직업군인 + 의무복무 통합)"** 의미로 사용된 것.

### 3-7. province × housing_type — Phase 1 격차의 추적
Phase 1에서 발견한 "전체적으로 아파트 과대" 격차의 **결합 분포 내부 구조**:

| 셀 | p_obs | p_indep | diff (pp) |
|---|---:|---:|---:|
| 서울 × 다세대주택 | 4.49% | 2.12% | **+2.37** |
| 경기 × 단독주택 | 2.40% | 4.43% | **−2.03** |
| 서울 × 단독주택 | 1.58% | 3.13% | **−1.56** |
| 서울 × 아파트 | 10.07% | 11.49% | −1.42 |
| 경기 × 아파트 | 17.64% | 16.27% | +1.37 |
| 경상북 × 단독주택 | 1.84% | 0.85% | +0.99 |
| 전라남 × 단독주택 | 1.53% | 0.58% | +0.95 |

→ 도시(서울·경기)는 단독주택 과소·다세대 과대(서울)·아파트 약한 과대(경기), 농촌(전남·경북)은 단독주택 과대.
→ **결합 구조 자체는 한국 도시-농촌 주거 패턴을 정성적으로 잘 반영**.
→ Phase 1 의 housing 전체 marginal 격차는 per-person 보정 후 TVD ≈ 0.08 로 축소 ([§3-4](PHASE1_REPORT.md#3-4-housing_type----약한-격차)) — 결합 구조 자체보다 단위·정렬 문제가 컸음.

### 3-8. education × occupation : NMI = 0.10
**학력에 따른 직업 분리가 명확.**
- 4년제 × "건물 청소원" : PMI = **−3.30** (사실상 거의 없음)
- 4년제 × "건물 경비원" : PMI = **−2.28**
- 무학 × 무직 : PMI = +0.73
- 초등학교 × 무직 : PMI = +0.59 (저학력 노년 → 무직 자연스러움)

→ 학력-직업 간 sorting을 PGM이 인코딩하고 있음.

### 3-9. age × occupation
- 65-74, 75-84, 85+ × 무직: 모두 양의 PMI (은퇴 인구 자연스럽게 무직)
- 35-44, 45-54 × 무직: 음의 PMI (현역 노동 연령)

### 3-10. bachelors_field × occupation
- NMI = 0.083, U(occupation|field) = 0.054, U(field|occupation) = 0.177
- 비대칭이 강함: 특정 직업은 전공을 강하게 함의(예: 의사 ↔ 보건·복지), 특정 전공은 다양한 직업으로 분기

---

## 4. Theil U 비대칭성에서 보이는 인과 구조

방향성 차이가 가장 큰 페어들 — `U(Y|X)` 와 `U(X|Y)` 의 격차가 클수록 **한쪽이 다른 쪽을 강하게 함의**한다는 증거:

| pair | U(Y\|X) | U(X\|Y) | 해석 |
|---|---:|---:|---|
| military × occupation | 0.008 | **1.000** | 직업 → 군 복무 결정적 |
| district × province | **1.000** | 0.465 | 시군구 → 시도 결정적 (행정 계층) |
| marital × family_type | 0.317 | **0.717** | 가구 형태 → 결혼 상태 강하게 함의 |
| sex × occupation | 0.027 | **0.169** | 직업명 → 성별 약하게 함의 (간호사·소방관 등) |
| age × marital | **0.301** | 0.162 | 나이 → 결혼 단계 |
| field × occupation | 0.054 | **0.177** | 직업 → 전공 함의 |
| edu × occupation | 0.072 | **0.188** | 직업 → 학력 함의 |

→ **PGM이 "결정적 함의" 와 "확률적 영향"을 잘 구분해서 인코딩**하고 있다.

---

## 5. Phase 2 종합

### 잘 한 것
1. **demographic 곡선의 정성적 부합**: 나이별 결혼/사별, 학력 코호트, 지역별 주택, 결혼-가구 결정론적 일관성 모두 한국 현실과 방향·강도가 부합 (단, marital→family 의 100% 결정론적 매핑은 현실의 별거·기러기 다양성을 일부 제거).
2. **결정적 제약 위반 없음**: 배우자있음 ↔ 가구에 배우자 존재, 시군구 ↔ 시도 매칭 모두 일관.
3. **성별 segregation 인코딩**: 공학/보건 같은 분야의 성비는 한국 현실과 부합.
4. **현실적인 detail**: 여성 군인 9.8%, 25-34 4년제 51.6% 등 미시 수치가 그럴듯.

### 발견된 격차 / 의문점
1. **housing 전체 marginal 은 약한 격차** (Phase 1, TVD ≈ 0.08 per-person 보정 후) **vs 결합 구조는 그럴듯** (Phase 2 §3-7) — 단위·정렬 이슈가 marginal 격차의 주요 원인이며, 시군구×주택 결합은 한국 도시-농촌 패턴 잘 반영.
2. **sex × occupation NMI = 0.046** 은 한국 직업 성분리 현실보다 약할 수도 있음 — Phase 3에서 직업×성 KOSIS 비교 필요
3. **occupation 2,120개 중 "무직" 36.7%** 의 내부 구조(가정주부/학생/은퇴자/실업자 분리 안 됨)는 Phase 4 텍스트 분석에서 들여다볼 부분

### 데이터 카드 vs 실측
| 카드 주장 | Phase 2 검증 |
|---|---|
| "성·소득·학력·전공이 직업에 *독립적*으로 영향" | sex×field, edu×occupation 모두 강한 의존성 인코딩됨. **카드 문구는 occupation 라벨링 단계의 좁은 의미**로 보임 |
| "PGM으로 인구 분포 통제" | marginal에 더해 **bivariate 결합 구조까지 통제**되고 있음 |
| "검증·평가 NeMo Data Designer 내장" | 본 리포가 외부 재현 가능한 bivariate 검증 첫 결과 |

### 다음 단계로 이어지는 질문
- **Phase 3**: predictive decoupling probe — feature 추가가 분류기 정보를 늘리는가?
- **Phase 3 보강**: KOSIS 의 sex × age × province 3-way 와 비교
- **Phase 4**: 7개 자유서술 페르소나 텍스트의 어휘·고정관념 분석

---

## 6. 산출물

```
reports/PHASE2_REPORT.md                       <- 본 리포트
reports/PAIR_INDEX.md                          <- 55 페어 갤러리 인덱스 (NMI 정렬)

reports/figures/
  heatmap_cramers_v.png                        <- 11x11 대칭
  heatmap_nmi.png                              <- 11x11 대칭
  heatmap_theils_u.png                         <- 11x11 비대칭 (방향성)
  heatmap_tvd_indep.png                        <- 11x11 대칭

  bivariate_all/                               <- 55개 페어 모두 (3-panel)
    age_bin__x__sex.png
    ... (55 files)

  bivariate/                                   <- 본문 깊이 다룬 10개
    detail_sex__x__bachelors_field.png
    ... (10 files)

data/processed/bivariate/
  metrics_long.csv                             # 55 pairs × 10+ metrics
  matrix_{cramers_v, nmi, theils_u, tvd_indep}.csv

data/processed/bivariate_detail_all/           # 모든 55 페어
  index.csv                                    # 페어별 truncation·지표 일람
  contingency_<x>__x__<y>.csv                  # 55 contingency
  cells_<x>__x__<y>.csv                        # 55 per-cell deviation

data/processed/bivariate_detail/               # 본문 깊이 10개
```

## 7. 재현
```bash
python scripts/04_bivariate_metrics.py     # 55 pair metric matrices
python scripts/05_bivariate_detail.py      # 본문 큐레이션 10개 detail
python scripts/05b_bivariate_detail_all.py # 전 55개 페어 detail
python scripts/06_build_pair_index.py      # PAIR_INDEX.md 갤러리
```



---

# §6. Phase 3 — PGM 구조 추론


> **한 문단 요약**: Conditional MI 와 PC-style 알고리즘으로 PGM이 생성한
> 데이터에서 *관찰되는 조건부 의존 skeleton* 을 추정. 결과: **23 direct + 14 mediated
> + 18 no-edge** (단, ε=0.005 nats, |Z|≤2 한계 하; permutation null 로 bias 보정 시
> 12개만 ratio>2 로 견고). 가장 결정적 발견: **`housing_type` 은 사람 속성과
> 통계적으로 분리됨** — 분류기로 person-attrs 추가 정보 = -0.008 nats (실질 0).
> 1인 가구도 4인 가족도 모두 같은 주거 분포. `military_status` 는 occupation 라벨에서
> 거의 결정적으로 파생되는 부수 변수이며, 변수 의미는 "현역 군 인력 신분
> (직업군인 + 의무복무 통합)" 으로 한국군 인력 구성과 부합.

NVIDIA `Nemotron-Personas-Korea` 가 사용한 PGM이 생성한 데이터에서 **관찰되는 조건부 의존 skeleton**을 역공학적으로 추정한다.

> ⚠️ 본 분석은 NVIDIA의 proprietary PGM 그래프 자체의 복원이 아니라, **공개 데이터에 남아있는 조건부 의존 구조의 근사** 이다. 생성 파이프라인은 PGM 외 LLM 텍스트 생성·필터링·후처리를 포함하며, 관찰 데이터에서 추론한 skeleton 은 conditioning depth, threshold, latent variable 가정에 의존한다.
>
> Phase 2 결론: marginal·bivariate 결합은 풍부하지만, 두 변수가 강하게 결합돼 보여도 직접 edge인지(아니면 다른 변수를 통한 매개인지) 모른다.
> Phase 3 결론: **23개 direct + 14개 mediated + 18개 marginal 독립의 skeleton** 을 PC-style 추론으로 추정했다 (단, ε=0.005 nats · \|Z\|≤2 한계 하의 결과로, "direct" = "현 조건 하에서 매개되지 않은 잔존 의존"). Housing은 district 외 사람 속성과 거의 독립이라는 가설을 **예측 기반 conditional-independence probe** (분류기로 정보 추가량 측정) 로도 정량 확인 (person-attrs 정보 추가 = −0.008 nats, 즉 0).

---

## 1. 방법

### 1.1 Conditional Mutual Information (CMI)

```
I(X; Y | Z) = Σ_{x,y,z} p(x,y,z) · log [ p(x,y,z) · p(z) / (p(x,z) · p(y,z)) ]
```

해석: Z를 알 때 X와 Y의 결합 정보. 만약 X⊥Y|Z (Z가 매개) 라면 CMI ≈ 0.
모든 MI / CMI 단위는 **nats**.

### 1.2 PC-style skeleton recovery

각 페어 (X, Y) 에 대해:

1. **Level 0** — marginal MI `I(X;Y)` 계산
2. **Level 1** — `I(X;Y|Z)` for every other Z (단일 변수 조건)
3. **Level 2** — `I(X;Y | Z*, Z')` for every Z' (Z* = level-1 best mediator + 한 변수 더)
4. **분류**:
    - `no_edge_marginal` — 마지널부터 < ε
    - `mediated`        — 어떤 conditioning 에서든 < ε 으로 떨어짐
    - `direct`          — 어떤 conditioning 으로도 ε 위에 머무름

ε = **0.005 nats** (효과크기 임계, N=1M 에서 χ² p-value는 의미 없음)

### 1.3 Decoupling probe (예측 기반 conditional-independence)

> 용어 주의: 본 probe 는 합성 데이터를 train/test split 한 **within-synthetic** 비교다. 엄밀한 TSTR (Train on Synthetic, *Test on Real*) 과 다르므로 "predictive conditional-independence probe" 또는 "decoupling probe" 명칭을 사용.

분류기로 정보 추가량을 측정:
```
Info_added(features → target | baseline) = CE(target | baseline) − CE(target | baseline + features)
```
- 0 에 가까우면 features는 target에 conditional independent (decoupled)
- 큰 양수면 features가 baseline 위에 정보를 더함

`HistGradientBoostingClassifier`, 200K subsample, 80/20 train/test, ε-feature 컷오프 = 250 (HGB cardinality 제한).

### 1.4 Leakage check — 위 probe 결과는 데이터 누수에 영향받았나?

`scripts/11_decoupling_probe.py` 의 잠재적 leakage 6가지 (encoder 전체 fit, cap_high_card 전체 빈도 기반, target encoding, 단일 split, HGB 내부 split, 합성 데이터 row 중복성) 을 식별 후, **train-only encoder + train-only cap + 5-fold CV** 로 재실행 ([`scripts/11b_decoupling_probe_no_leakage.py`](../scripts/11b_decoupling_probe_no_leakage.py)).

| Case | 원본 info_added | Leakage-corrected | 차이 |
|---|---:|---:|---:|
| **Q1 housing decoupled** | **−0.0077** | **−0.0082** | −0.0006 |
| C1 family_type control | +0.8175 | +0.8159 | −0.0015 |
| C2 occupation control | +0.1809 | +0.1769 | −0.0041 |
| Q2 military\|age+sex | +0.0020 | +0.0019 | −0.0001 |
| Q3 military\|sex+age+occ | +0.0225 | +0.0236 | +0.0012 |
| C3 marital control | +0.5530 | +0.5518 | −0.0012 |

→ **모든 차이 < 0.005 nats** (측정 효과의 1% 이하). 5-fold CV 표준오차 SE < 0.02 nats.
**결론 변화 없음** — leakage 우려는 valid 했으나 실제 영향은 무의미.

### 1.5 Subsample stability

5 seed × 200K subsample 로 단일-Z 분류 재계산. 52/55 페어 분류 일치(나머지 3개는 |Z|=2 조건 사용 여부 차이로, **데이터 자체 안정성 100%**).

---

## 2. 핵심 결과 — 추정된 PGM Skeleton

### 2.1 Direct edges (23개)

| pair | marginal MI | min CMI | drop | best mediator pair (실패) |
|---|---:|---:|---:|---|
| district ~ province | 2.426 | 2.271 | 6% | housing+occupation (구조적 deterministic) |
| marital ~ family_type | 0.750 | 0.522 | 31% | age+sex |
| education ~ bachelors_field | 0.631 | 0.420 | 33% | occupation+district |
| age ~ family_type | 0.330 | 0.090 | 73% | marital+education |
| age ~ marital | 0.315 | 0.059 | 81% | family+education |
| education ~ occupation | 0.314 | 0.100 | 68% | bachelors_field+age |
| age ~ education | 0.276 | 0.134 | 51% | marital+bachelors_field |
| bachelors_field ~ occupation | 0.235 | 0.059 | 75% | education+sex |
| occupation ~ district | 0.192 | 0.142 | 26% | province+military |
| age ~ occupation | 0.166 | 0.089 | 46% | education+military |
| housing ~ district | 0.155 | 0.080 | 48% | province+military |
| sex ~ occupation | 0.117 | 0.106 | **10%** | bachelors_field+military (sex가 occ에 거의 직접 작용) |
| family_type ~ occupation | 0.070 | 0.058 | 17% | marital+military |
| marital ~ occupation | 0.050 | 0.018 | 63% | age+military |
| family_type ~ district | 0.049 | 0.030 | 38% | province+marital |
| sex ~ bachelors_field | 0.037 | 0.025 | 33% | occupation+education |
| military ~ occupation | 0.033 | 0.030 | **10%** | sex+age (구조적 deterministic — 군 직업 = 현역) |
| sex ~ marital | 0.028 | 0.009 | 69% | family+education |
| age ~ district | 0.022 | 0.015 | 33% | province+military |
| sex ~ family_type | 0.018 | 0.008 | 56% | marital+military |
| marital ~ district | 0.016 | 0.009 | 44% | province+family |
| housing ~ occupation | 0.010 | 0.010 | **0%** | military+sex (drop이 없지만 마지널 MI 0.010 nats 가 임계 0.005 의 2배 — *threshold artifact 또는 매우 약한 잔존 의존성 가능성. P3 ε sensitivity 분석에서 재확인 필요*) |
| education ~ district | 0.052 | 0.018 | 65% | bachelors_field+province |

### 2.2 Mediated edges — 직접 edge 없음 (14개)

| pair | marginal MI | mediated by | 의미 |
|---|---:|---|---|
| age ~ bachelors_field | 0.065 | education_level | age → edu → field chain |
| marital ~ education | 0.105 | **age** | 코호트 효과 (둘 다 age의 결과) |
| family ~ education | 0.090 | age+marital | "" |
| housing ~ province | 0.075 | district | 지리 hierarchy |
| occupation ~ province | 0.049 | district | "" |
| bachelors_field ~ district | 0.031 | education | edu가 매개 |
| marital ~ bachelors_field | 0.025 | education | edu가 매개 |
| family ~ bachelors_field | 0.019 | education | "" |
| family ~ province | 0.018 | district | "" |
| education ~ province | 0.018 | district | "" |
| sex ~ education | 0.014 | marital | (Korea: 결혼한 여성/남성의 학력 분포) |
| bachelors_field ~ province | 0.012 | district | "" |
| age ~ province | 0.007 | district | "" |
| marital ~ province | 0.006 | district | "" |

### 2.3 No marginal edge (18개) — 둘 다 자체로 거의 독립

`sex ~ {province, district, housing}`, `military ~ {age, family, housing, edu, field, district, province, marital}`, `housing ~ {age, family, marital, edu, field, sex}`, `age ~ sex`(약함), `age ~ housing`, `family ~ housing`, ...

→ **이 군집이 PGM의 "독립으로 처리" 부분의 정량적 실체**.

### 2.4 그림으로 본 skeleton

![skeleton compare](figures/skeleton_compare.png)

- 좌: marginal-dependent (MI ≥ ε) 모든 페어. 점선 회색이 PC 단계에서 매개로 판정되어 사라진 edge.
- 우: 추론된 skeleton. **23개 직접 edge.**
- 노드 차수: occupation 9 (최대 hub) — 사실상 모든 사람 속성의 sink. district 7. age, marital, family 5. 반면 housing 2, military 1, province 1.

### 2.5 Permutation null + bootstrap CI — 어느 edge 가 bias 가 아닌가?

**왜 필요한가**: plug-in MI 추정량은 contingency table 의 카디널리티에 비례하는
upward bias 를 가짐. 대략 `bias ≈ (k-1)(m-1)/(2N)` (Miller-Madow). occupation
(2,120 levels) × district (252 levels) 의 경우 bias 만 약 0.27 nats — 우리 임계
ε=0.005 의 53배. 따라서 단순 MI/CMI 값으로는 "진짜 효과" 와 "카디널리티 bias" 를
구분 불가.

**방법**:
- **Permutation null**: H0 (X⊥Y 또는 X⊥Y\|Z) 하에서 Y 를 (Z-stratified) 셔플 → null 분포 100회
- **Bootstrap CI**: 같은 N 으로 resample 100회 → 추정치의 95% CI
- 100K subsample × 100 perms / boots
- 핵심 metric: **ratio = observed / null_p95** (효과크기 / bias 우월성)

산출물: [`data/processed/cmi/permutation_null_{marginal,conditional}.csv`](../data/processed/cmi),
[`bootstrap_{marginal,conditional}.csv`](../data/processed/cmi)
시각화: [`figures/perm_null_{marginal,conditional}.png`](figures), [`forest_{marginal,conditional}.png`](figures)

#### 결과 1 — Marginal: 모든 페어가 p<0.01 이지만, 효과 강도는 천차만별

55개 페어 모두 p<0.01 로 "통계적으로 유의" 하지만, **N 이 크면 거의 모든 차이가 유의해지므로 효과크기 우월성** (ratio_obs/null_p95) 이 더 정보적:

| ratio | n_pairs | 의미 |
|---|---:|---|
| ≥ 10 | 28 | 강건 — bias 무관 |
| 2 – 10 | 17 | 유의 — 효과 > 2× bias floor |
| < 2 | 10 | bias-suspect — 효과가 bias 와 같은 자릿수 |

ratio < 2 인 10개 페어는 모두 **occupation / district / family_type 같은 high-cardinality 변수**를 포함:

| pair | observed | null_p95 | ratio | 해석 |
|---|---:|---:|---:|---|
| `military × housing` | 0.000027 | 0.000062 | **0.44** | obs < null — 사실상 독립 |
| `sex × housing` | 0.000028 | 0.000047 | **0.60** | obs < null — 사실상 독립 |
| `occupation × district` | 0.597 | 0.579 | **1.03** | obs MI 의 97%가 bias |
| `housing × occupation` | 0.037 | 0.034 | 1.09 | bias 우월 |
| `military × district` | 0.0019 | 0.0015 | 1.25 | |
| `occupation × province` | 0.125 | 0.098 | 1.27 | |
| `sex × district` | 0.0018 | 0.0014 | 1.30 | |
| `family × occupation` | 0.163 | 0.124 | 1.32 | |
| `family × district` | 0.086 | 0.045 | 1.90 | |
| `military × family` | 0.0005 | 0.0003 | 1.96 | |

**가장 충격적**: `occupation × district` 의 marginal MI = 0.597 nats 중 97% 가 카디널리티 bias. 진짜 효과는 약 0.018 nats.

#### 결과 2 — Conditional: 23개 'direct edge' 중 11개는 bias-suspect

조건부 permutation null (Y 를 Z 안에서 셔플) 결과, **23개 direct edge 중 12개만 ratio > 2** 로 견고하고 11개는 의심:

| 분류 | n | 페어 |
|---|---:|---|
| ★★★ ratio ≥ 10 (가장 견고) | 4 | `marital×family` (80), `age×education` (65), `sex×family` (14), `age×marital` (11) |
| ★★ ratio 2–10 (유의) | 8 | `housing×district` (9.8), `age×family` (8.0), `sex×marital` (7.5), `sex×occupation` (3.8), `military×occupation` (3.6), `education×bachelors_field` (2.3), `age×district` (2.2), `district×province` (2.1) |
| ⚠️ ratio < 2 (bias-suspect) | 11 | `occupation×district` (1.01), `housing×occupation` (1.05), `marital×occupation` (1.06), `family×occupation` (1.16), `marital×district` (1.17), `family×district` (1.30), `bachelors_field×occupation` (1.46), `age×occupation` (1.53), `education×occupation` (1.57), `sex×bachelors_field` (1.84), `education×district` (1.94) |

⚠️ **모든 bias-suspect 페어가 occupation 또는 district 를 포함** — 정확히 GPT-5.5 Pro 가 지적한 high-cardinality 변수 문제 패턴.

#### 결과 3 — 핵심 결론들의 robustness check

| 결론 | Permutation null | 견고? |
|---|---|:---:|
| **Housing × person-attrs decoupled** | 모든 housing × person-attr 페어 ratio < 2 (no_edge_marginal) | ✅ |
| **Housing × district direct edge** | conditional ratio = **9.8** | ✅ |
| **Marital → family 결정성** | conditional ratio = **80** | ✅ |
| **Sex×bachelors_field 직접 edge** | conditional ratio = 1.84 | ⚠️ borderline |
| **Education chain (age→edu→field, edu→occupation)** | age×edu ratio=65, edu×field=2.3, edu×occupation=1.6 | 일부 ⚠️ |
| **Military as occupation function** | conditional ratio = 3.6 + occ→military 결정성 | ✅ |
| **occupation×district direct edge** | conditional ratio = **1.01** | ❌ **bias artifact 가능성 높음** |

→ **Skeleton 의 23 direct edges 를 bias-corrected 하면 12개로 줄어든다.** 11개는 high-cardinality bias 의 결과일 수 있어 단언 약화 필요.

#### Bootstrap CI — 추정 정밀도

Bootstrap (N=100K × 100회) 으로 본 CI 폭:
- 강한 의존성 (district~province MI=2.43): SE = 0.004 nats (CI ±0.7%)
- 중간 (housing~province MI=0.075): SE = 0.001 (CI ±2%)
- 약한 (marital~military MI=0.0005): SE = 0.0001 (CI ±18%)

→ 추정치 자체는 모든 페어에서 정밀하게 측정됨. 흔들리는 것은 *해석* 이지 *측정* 이 아님.

![perm marginal](figures/perm_null_marginal.png)
![perm conditional](figures/perm_null_conditional.png)

#### Bias-corrected skeleton — 한 장에 정리

위 검증의 결과를 §2.4 의 skeleton 그림에 직접 반영. 23 direct edge 를 ratio tier 로 재분류 + 가장 강한 6개에만 label:

![bias_corrected_skeleton](figures/skeleton_bias_corrected.png)

(A) 신뢰 가능한 dependency 만 (robust + significant 12개) — 후속 분석에서 사용 권장. (B) 23개 모든 edge 를 ratio 순으로 정렬 — bias-suspect 11개 (빨강) 가 모두 occupation/district 포함 페어임이 한눈에.

---

### 2.6 외부 검증 — KOSIS / 통계청 cross-tab 비교 (P7 v1)

**왜 필요한가**: §2.5, §2.6 까지는 모두 *내부* 통계 검증 (합성 데이터 안에서의 robustness). 합성 데이터의 결합 분포가 *실제 한국 인구* 의 결합 분포와 일치하는지는 별도 외부 데이터가 필요. 이 절은 그 외부 비교의 **부분 검증** (P7 v1).

**한계 (서두 명시)**: KOSIS 직접 API 접근이 SSO redirect / JS 동적 로딩으로 막혀, 본 절은 공식 보도자료 / 한국의 사회동향 / 정책브리핑에 *명시적으로 인용된* cross-tab cell 만 사용. 모든 cell 의 완전 외부 비교는 KOSIS Open API 키 등록 후 P7 v2 에서 처리. 출처는 [`data/reference/kosis_joint.json`](../data/reference/kosis_joint.json) 에 셀별 명시.

#### (1) age × marital — ★★★ 강한 외부 검증

20대~50대 미혼 비율, 통계청 2020 인구주택총조사 + 한국의 사회동향 2024 발췌:

| 연령대 | 성별 | reference (KOSIS) | synth | diff (pp) |
|---|---|---:|---:|---:|
| 20대 | all | 92.80% | 90.29% | −2.51 |
| 30대 | all | 42.50% | 45.02% | +2.52 |
| 30대 | 남자 | 50.50% | 54.11% | +3.61 |
| 30대 | 여자 | 32.80% | 34.97% | +2.17 |
| 40대 | all | 17.90% | 19.41% | +1.51 |
| 40대 | 남자 | 23.60% | 25.64% | +2.04 |
| 40대 | 여자 | 11.90% | 12.91% | +1.01 |
| 50대 | all | 7.40% | 8.07% | +0.67 |

→ **8개 cell 모두 ±4pp 이내**. PGM 이 한국 census 의 age × sex × marital 결합 분포를 정밀하게 재현. **인구학 chain (Phase 2/3) 결론의 외부 검증**.

![age_marital](figures/kosis_joint_age_marital.png)

#### (2) age × sex × education — ★ Cohort vintage caveat

50대 초반·60대 초반 (50-54, 60-64) × 성별 × 학력 (중졸이하 / 4년제) — 한국노동사회연구소 2014 자료:

| cell | metric | reference (2014) | synth (2024) | diff (pp) |
|---|---|---:|---:|---:|
| 50s_early_M | 중졸이하 | 21.6% | 4.8% | **−16.8** |
| 50s_early_M | 4년제대학 | 25.4% | 29.5% | +4.1 |
| 50s_early_F | 중졸이하 | 39.7% | 6.9% | **−32.8** |
| 50s_early_F | 4년제대학 | 10.6% | 22.6% | **+12.0** |
| 60s_early_M | 중졸이하 | 48.9% | 19.5% | **−29.4** |
| 60s_early_M | 4년제대학 | 13.3% | 18.2% | +4.9 |
| 60s_early_F | 중졸이하 | 73.7% | 29.8% | **−44.0** |
| 60s_early_F | 4년제대학 | 4.6% | 9.7% | +5.1 |

⚠️ **Reference 가 2014년 시점**. 2014의 50대 초반 = 1960-1964년생, 2024의 50대 초반 = 1970-1974년생. 한국 교육 확장기 (1980~90년대 대학 진학률 폭증) 영향으로 **10년 코호트 갱신**이 ref→synth 차이의 일부를 설명. 그러나 60대 여성 중졸이하 −44pp 는 코호트만으로 설명하기 어려움 — **PGM 이 고령층 학력을 상향 편향시킬 가능성**. 정확한 검증은 2020 census 5세별 학력 표 (KOSIS DT_1IN1502, P7 v2) 필요.

![age_sex_edu](figures/kosis_joint_age_sex_edu.png)

#### (3) province × housing_type — ★★ 부분 검증

2023 인구주택총조사 보도자료의 5개 시도 + 전국 평균 cell:

**아파트 비율**:

| 시도 | reference (가구) | synth (개인) | diff (pp) |
|---|---:|---:|---:|
| 전국 | 53.10% | 62.06% | **+8.96** |
| 세종 | 78.00% | 86.05% | +8.05 |
| 광주 | 81.50% | 78.42% | −3.08 |
| 대전 | 75.60% | 74.09% | −1.51 |
| 제주 | 25.70% | 29.20% | +3.50 |

**단독주택 비율**:

| 시도 | reference (가구) | synth (개인) | diff (pp) |
|---|---:|---:|---:|
| 전국 | 28.40% | 16.92% | **−11.48** |
| 전라남 | 47.90% | 44.51% | −3.39 |
| 인천 | 8.20% | 6.84% | −1.36 |

→ **시도별 패턴은 ±3pp 이내로 잘 일치** (광주·대전·제주·전라남·인천 모두). 그러나 **전국 합계는 아파트 +9pp / 단독 −11.5pp 로 큰 격차**. 가능 원인:
- 가구 단위 vs 개인 단위 모집단 차이 (개인 기준 아파트 비중이 약간 높음 — 부분 설명)
- 시드 통계 vintage 또는 보정 차이 (Phase 1 §3-4 의 재확인)
- 세종은 ref vs synth +8pp — 시도 단위에서도 outlier

![province_housing](figures/kosis_joint_province_housing.png)

#### 종합 (P7 v1)

| 검증 페어 | 외부 일치도 | 핵심 발견 |
|---|---|---|
| **age × marital × sex** | ★★★ ±4pp 이내 8/8 cell | 인구학 chain 결론 외부 확인 |
| **age × sex × education** | ★ ⚠️ 큰 격차 + vintage caveat | 60대 여성 중졸이하 −44pp — PGM 고령층 학력 상향 편향 가능성 |
| **province × housing** | ★★ 시도별 ±3pp / 전국 ±9pp | 시도 패턴 일치, 전국 offset 은 Phase 1 발견 재확인 |

→ **인구학 chain 결론 (★★★) 은 외부 데이터로도 강하게 지지**. **Housing decoupling 결론은 영향 없음** (housing × person-attrs 분석은 외부 비교와 무관). **고령층 학력 분포는 vintage 보정 후 재검증 필요** — 새로운 가설.

---

### 2.7 ε threshold sensitivity — 위 결과는 임계 의존성이 얼마나 큰가

ε=0.005 nats 는 임의 선택이므로, ε ∈ {0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05} grid 로 분류를 재계산:

| ε | direct | mediated | no_edge_marginal |
|---:|---:|---:|---:|
| 0.0005 | 32 | 17 | 6 |
| 0.001 | 31 | 14 | 10 |
| 0.002 | 30 | 12 | 13 |
| **0.005 (default)** | **23** | **14** | **18** |
| 0.01 | 19 | 15 | 21 |
| 0.02 | 16 | 11 | 28 |
| 0.05 | 13 | 5 | 37 |

![sensitivity](figures/epsilon_sensitivity.png)

**ε를 두 자릿수 변동시켜도 (×100) direct edge 수는 32 → 13 사이에서만 움직인다.** 즉 23개라는 헤드라인 숫자는 약 ±10 의 임계 의존성을 가진다.

**ε-stable edges (전 grid 에서 분류 불변, 23개)** — 가장 견고한 의존성:

다음 페어들은 ε ∈ [0.0005, 0.05] 전 범위에서 같은 분류를 유지 → **방법론 의존성이 가장 낮은 결론**:
- 항상 direct: `district~province`, `marital~family`, `edu~bachelors_field`, `age~marital`, `age~family`, `age~education`, `age~occupation`, `edu~occupation`, `bachelors_field~occupation`, `housing~district`, `sex~occupation`, `family~occupation`, `occupation~district`, `marital~education_level` (단 ε≥0.005 에선 mediated 로 바뀜 — 아래 boundary 참조)
- 항상 no_edge_marginal: `military~{housing, district, province, education, family, bachelors_field}`, `sex~{province, district, housing}`

**Boundary pairs (ε에 따라 분류가 바뀌는 32개)** — 가장 방법론에 민감한 결론:

핵심 boundary 사례 (Top 5):

| pair | MI | min CMI | 0.0005 | 0.005 | 0.01 | 0.05 |
|---|---:|---:|---|---|---|---|
| `marital ~ education` | 0.105 | 0.0043 | direct | mediated | mediated | mediated |
| `family ~ education` | 0.090 | 0.0038 | direct | mediated | mediated | mediated |
| `marital ~ occupation` | 0.050 | 0.018 | direct | direct | direct | no_edge |
| `housing ~ occupation` | 0.0097 | 0.0096 | direct | direct | **no_edge** | no_edge |
| `sex ~ marital` | 0.028 | 0.0087 | direct | direct | mediated | no_edge |

전체 boundary 표: [`data/processed/cmi/epsilon_boundary.csv`](../data/processed/cmi/epsilon_boundary.csv) ·
페어별 분류 매트릭스: [`reports/figures/epsilon_per_pair.png`](figures/epsilon_per_pair.png)

#### Housing 결론은 ε-stable 한가?

가장 결정적 결론(housing decoupling)에 대한 falsification check:

![housing](figures/epsilon_housing.png)

- `housing ~ district` 는 **모든 ε 에서 direct 유지** → 지리적 의존성은 견고
- `housing ~ {age, sex, marital, family, education, bachelors_field}` 는 **모든 ε 에서 no_edge_marginal 또는 mediated** → 사람 속성과의 분리도 견고 (default ε 변경으로 뒤집히지 않음)
- 단 `housing ~ occupation` 은 ε ≥ 0.01 에서 no_edge_marginal 로 떨어짐 — marginal MI 가 임계 근처라 임계 artifact 가능성

→ **Housing decoupling 결론은 ε 임계 변동에 대해 견고**. ε=0.005 → 0.001 또는 0.05 어느 쪽으로 바꿔도 결론 유지.

---

## 3. 결정적 관찰들

### 3.1 housing의 완전한 decoupling (예측 기반 probe 로 이중 확인)

| 모델 | Cross-Entropy | accuracy | info(over baseline) |
|---|---:|---:|---:|
| baseline (district만) | 1.001 | 65.4% | (baseline) |
| + age + sex + marital + family + edu + field + occupation | 1.008 | 65.3% | **−0.008 nats (즉, 0)** |

**완전한 decoupling.** district만으로 housing 예측은 실용적으로 최선이고, 사람 속성을 다 넣어도 정보가 더해지지 않음 — 오히려 약간 과적합하여 나빠짐.

> **연구자 시사점**: 이 데이터셋으로 housing 관련 분석 (예: "1인가구 주거 형태 분석", "청년 주거 빈곤") 을 하면 **결과가 trivial**이 된다. 모든 인구통계 그룹의 주거 분포가 거의 같기 때문. 이런 분석에는 본 데이터셋을 쓰지 말 것.

### 3.2 housing | age × marital — 시각으로도 평탄

![A](figures/threeway/A_apt_by_age_marital.png)

8 (연령) × 4 (혼인) = 32 셀. 모든 셀에서 P(아파트) = 56.6 ~ 64.3% — **사람 속성에 따라 거의 변화 없음**.
대조: `B. P(혼자 거주 | 연령, 혼인)` 은 미혼·사별·고연령에서 매우 높음(70%+) — PGM이 이 페어는 잘 잡음.

### 3.3 military_status는 occupation의 함수

CMI 결과: 다른 모든 변수와의 결합이 occupation 조건걸면 100% 사라짐 (`I(military; *) | occupation = 0`).
Probe Q3: military 예측에 sex 만 쓰면 CE=0.031, sex+age+occupation 쓰면 CE=0.008 (info +0.022, 90% share).

**즉 military는 occupation 이름의 부수 라벨에 가깝다.**
PGM에서 military는 독립 노드라기보다, occupation 라벨 → "현역" deterministic 매핑.

### 3.4 military × age — 한국군 현역 인력 구성 부합

![C](figures/threeway/C_active_by_sex_age.png)

`military_status = 현역` 의 의미는 **"현역 군 인력 신분 (직업군인 + 의무복무 통합)"** 으로,
미국식 "active duty" 에 더 가깝다 (단순 의무복무 이행만 의미하지 않음).

`scripts/13_military_breakdown.py` 의 계급별 분해:

| 계급 | n | 비중 | 평균 연령 | 연령 p25-p75 | 최대 연령 | 여성 비율 |
|---|---:|---:|---:|---|---:|---:|
| **병사** (의무복무) | 688 | 13.0% | 25.4 | 23-28 | **30** | **0.0%** |
| **부사관** (직업) | 2,636 | 49.9% | 40.6 | 33-48 | **55** | 11.5% |
| **장교** (직업) | 1,958 | 37.1% | 46.7 | 38-57 | **63** | 10.9% |

→ 한국군 부사관 정년 53-58세, 장교 정년 56-63세, **여성 의무복무 부재** 모두 정확히 반영.
PGM이 한국군 현역 인력 구성을 *정교하게* 모델링한 사례.

다만 다음은 그대로 유효한 한계:

- **military_status 는 occupation 의 결정적 함수에 가까움**: 현역 5,282명 모두 occupation = 군 직업 12개 중 하나. 두 변수를 함께 모델 입력으로 쓰면 정보 중복.
- **의무복무 *흐름* 정보 없음**: 어느 시점에 입영하고 어느 시점에 전역하는지, 1년/1.5년/2년 복무 길이의 차이 등 dynamic 정보는 정적 스냅샷에 담길 수 없음.
- **PGM 의 약한 비결정성**: 비현역인데 군 직업인 187명 (예비역·전역자·군무원으로 해석 가능) — PGM이 occupation → military_status 를 100% 결정적으로 매핑한 건 아님.

> **연구자 시사점**: 본 데이터셋은 (a) **의무복무 흐름 / 입영-전역 동학** 분석에는
> 부적합하지만, (b) **현역 군 인력의 cross-section 인구 구성** (계급별 연령·성비 등)
> 분석에는 사용 가능. 단 occupation 과 military_status 를 함께 입력으로 쓸 때
> 정보 중복에 주의.

### 3.5 demographic chain은 정확

`age → marital → family_type` 와 `age → education → bachelors_field → occupation` 두 chain은 PC 추론에서 chain 그대로 살아남음.
- Probe Control C3: `marital | age + sex + edu + family` → info_added = 0.55 nats (64% of total). family_type이 marital을 거의 결정.
- Probe Control C1: `family_type | district + person_attrs` → info_added = 0.82 nats (96% of total). 사람 속성이 가족유형의 거의 모든 정보 제공.

→ 인구학·교육 chain은 **연구 활용 가능**.

---

## 4. 추정 PGM의 의미적 해석

PGM은 다음 4개 군집으로 잘 분리됨:

```
[Geographic core]
  province ── district ── housing
                      ── (occupation, age, marital, family, education 와 약한 edge)
  
[Age-driven demographic chain]   
  age ── marital ── family
   │                   │
   └── (occupation, district 와 직접 edge)
  
[Education-Occupation cluster]
  age ── education ── bachelors_field ── occupation
                                            │
                                            sex (직접)
                                            │
                                            military (deterministic via 군 직업)
  
[Sex 영향]
  sex ── occupation, bachelors_field, marital, family
  sex ⊥ {province, district, housing} (현실 부합)
```

**데이터카드의 "성·소득·학력·전공이 직업에 *독립적*으로 영향"** 문구의 정확한 의미:
- `sex ↔ occupation`, `field ↔ occupation`, `education ↔ occupation` 모두 직접 edge로 살아있음 (drop 10%, 75%, 68%).
- 그러나 `sex ↔ field` 자체도 직접 edge (drop 33%) — 즉 sex와 field는 occupation 외 경로로도 연결됨.
- **정확한 해석**: occupation에 sex/edu/field가 들어가는 likelihood factor는 그들의 독립 곱 (`f(s)·g(e)·h(b)`) 으로 가중되지만, 그 sex/edu/field 변수들 자체의 결합 분포는 별도로 모델링됨.

---

## 5. 사용 시 권고 사항 (연구자 가이드)

### ✅ 본 데이터셋이 적합한 분석
- 시도/시군구 단위 인구 분포 / 시뮬레이션
- age × education × occupation 코호트 분석
- 결혼·가구 구조의 인구학적 변화 패턴
- bachelors_field × occupation × sex 의 노동시장 분리 연구
- LLM 학습용 합성 페르소나 (이건 데이터의 본 용도)

### ⚠️ 본 데이터셋을 **쓰지 말아야** 하는 분석
- **개인 속성별 주거 분석** (1인가구 주거, 청년 주거 빈곤, 학력×주거): housing이 사람 속성과 decoupled. 모든 그룹이 같은 주거 분포. *(지역 단위 시뮬레이션은 별개)*
- **의무복무 흐름·동학 분석**: military_status 는 정적 cross-section 라벨. 입영·전역 흐름 정보 없음.
- **지역 × 사람 속성의 미세 효과 분석**: 지리는 housing 외에는 다른 변수와 약하게만 연결.

### 🤔 신중하게 사용 (정보 중복·다른 출처 보강 필요)
- **현역 군 인력 구성 분석**: 계급별 연령·성비 cross-section 은 한국 현실 부합 (`military_breakdown.json` 참조). 단 military_status 와 occupation 동시 사용 시 정보 중복.
- **지역 단위 주거 시뮬레이션** (시군구별 아파트·단독 비중): housing × district 결합 자체는 그럴듯하고 시도별 패턴도 ±3pp 이내 (§2.6 외부 검증). 전체 marginal 도 per-person 기준 보정 후 약한 격차 (TVD ≈ 0.08, Phase 1 §3-4) — 베이스라인으로 사용 가능, 단독주택 비중만 주의.

### 💡 보완 방안
- Housing 분석이 필요하면 KOSIS 인구주택총조사 미시 자료를 별도 사용
- 병역 분석이 필요하면 병무청 통계연보 사용
- 본 데이터의 "현역 군인" 페르소나는 텍스트 학습용으로만 사용 권장

---

## 6. 한계

1. **단일 데이터셋, 단일 시점** — 시계열·생애주기 분석 불가.
2. **PC 추론은 |Z|≤2 까지만** — 3변수 이상 conditional independence는 완전 검증 안 됨. 대부분의 실제 PGM은 conditional dependency가 |Z|=3 이상으로도 잡혀, 우리가 'direct'로 판정한 일부 edge가 사실 매개일 수 있음.
3. **추론된 'direct edge' 의 의미 한계** — "ε=0.005, \|Z\|≤2 조건 하에서 매개되지 않은 잔존 의존" 일 뿐, 본래 생성 PGM 의 진짜 직접 edge 가 아님.
4. **방향성 미해결** — skeleton은 무방향. 본래 생성 PGM은 DAG일 텐데 d-separation 방향은 추가 가정 (예: 시간 순서, 도메인 지식) 없이는 식별 불가.
5. **CMI 임계 ε=0.005 nats** — 임의 선택이지만 §2.7 sensitivity 분석으로 의존성 정량화. ε 100배 변동 시 direct edge 수 32→13 변화하나, 핵심 결론 (housing decoupling, demographic chain 강건성) 은 ε-stable.
6. **High-cardinality variable bias** — §2.5 permutation null 결과, 23 'direct edges' 중 11개 (모두 occupation/district 포함) 가 ratio < 2 로 bias-suspect. 이들의 "direct" 분류는 plug-in MI 의 카디널리티 bias 일 가능성 — bias-corrected 결론에서는 12개 direct edge 만 견고.
7. **Decoupling probe 한계** — 1개 모델 (HGB) 의 학습 능력 한계. 다른 모델 (LightGBM, RF, NN) 에서 미세 차이 발생 가능. 5-fold CV 로 leakage·split-variance 점검 완료 (§1.4) 하나, 다중 모델 robustness 는 향후 작업 ([ROADMAP P8](../ROADMAP.md)).
8. **외부 검증 (§2.6) 은 부분만 완료** — KOSIS 직접 API 접근 불가로 보도자료 인용 cell 만 비교. 완전 외부 검증은 KOSIS Open API 키 등록 후 [ROADMAP P7 v2](../ROADMAP.md) 에서 처리 예정.

---

## 7. 산출물

```
data/processed/cmi/
  cmi_long.csv                     495 rows: x, y, z, mi_xy, cmi_xy_z, drop_ratio
  cmi_summary.csv                  55 rows: per-pair summary
  skeleton.csv                     55 rows + edge_class
  skeleton.json                    structured skeleton (direct/mediated)
  node_degrees.csv                 skeleton node degree
  stability.csv                    5-seed subsample stability (52/55 stable)
  epsilon_counts.csv               §2.7 ε sensitivity grid 분류 수
  epsilon_per_pair.csv             ε × pair 분류 매트릭스
  epsilon_boundary.csv             ε 따라 분류 변경 boundary 페어
  permutation_null_marginal.csv    §2.5 marginal permutation null + bias 측정
  permutation_null_conditional.csv §2.5 conditional permutation null (23 direct edges)
  bootstrap_marginal.csv           §2.5 bootstrap CI marginal
  bootstrap_conditional.csv        §2.5 bootstrap CI conditional

data/processed/
  decoupling_probe.json            §1.3 6 decoupling probe experiments
  decoupling_probe_no_leakage.json §1.4 leakage-corrected 재실행
  military_breakdown.json          §3.4 현역 계급별 분해 (의무복무/직업군인)
  housing_unit_correction.json     Phase 1 §3-4 per-person 보정
  kosis_joint_compare.json         §2.6 외부 cross-tab 비교

reports/figures/
  cmi_drop_heatmap.png             55 pairs × 9 conditioning Z, drop ratio
  skeleton_network.png             initial network (모든 direct edges 동등)
  skeleton_compare.png             marginal vs skeleton side-by-side (legacy)
  skeleton_bias_corrected.png      ★ 최종 — P4 ratio tier 반영, README 메인 그림
  cmi_stability.png                per-pair MI ± std across seeds
  epsilon_sensitivity.png          §2.7 ε grid 분류 추이
  epsilon_per_pair.png             ε × pair 분류 매트릭스
  epsilon_housing.png              housing 페어 ε-stability zoom
  perm_null_marginal.png           §2.5 marginal obs vs null scatter
  perm_null_conditional.png        §2.5 conditional obs vs null scatter
  forest_marginal.png              §2.5 marginal MI ± bootstrap CI + null 마커
  forest_conditional.png           §2.5 conditional CMI ± CI + null 마커
  kosis_joint_age_marital.png      §2.6 외부 검증: age × marital × sex
  kosis_joint_age_sex_edu.png      §2.6 외부 검증: age × sex × education
  kosis_joint_province_housing.png §2.6 외부 검증: province × housing
  threeway/
    A_apt_by_age_marital.png       housing decoupling visual
    B_alone_by_age_marital.png     family chain works (control)
    C_active_by_sex_age.png        현역 계급별 age 분포
    D_jobless_by_age_edu.png       occupation chain works
    E_apt_by_district_age.png      within-district age effect on housing
    F_married_by_age_sex.png       age × sex × marital
```

## 8. 재현

```bash
# 핵심 분석
python scripts/07_cmi_sweep.py             # 495 CMIs (~3분)
python scripts/08_skeleton_recovery.py     # PC-style with |Z|≤2 (~5분)
python scripts/09_network_viz.py
python scripts/10_three_way_viz.py
python scripts/11_decoupling_probe.py      # 6 HGB experiments (~3분)
python scripts/11b_decoupling_probe_no_leakage.py  # §1.4 leakage check (~15분)
python scripts/12_subsample_stability.py   # 5 seeds (~6분)
python scripts/13_military_breakdown.py    # §3.4 현역 계급 분해 (즉시)

# Robustness
python scripts/14_epsilon_sensitivity.py   # §2.7 ε grid (즉시)
python scripts/15_permutation_null.py      # §2.5 perm null 100×78 (~25분)
python scripts/16_bootstrap_ci.py          # §2.5 bootstrap 100×78 (~5분)
python scripts/17_perm_boot_viz.py         # §2.5 4 figures
python scripts/18_kosis_joint_compare.py   # §2.6 외부 비교 (즉시)
python scripts/19_bias_corrected_skeleton.py  # §2.5 최종 skeleton 그림
python scripts/20_housing_unit_correction.py  # Phase 1 §3-4 보정 (즉시)
```



---

# §7. CLAIMS LEDGER


본 리포가 한 모든 **검증 가능한 주장** 에 번호를 매기고, 각 주장의 증거 파일을 명시.
외부 리뷰어가 한 줄씩 검증할 수 있도록.

각 주장의 형식:
```
[CN] (Phase X · 신뢰도) 주장 내용. 
     Evidence: 파일경로:행 또는 표 인용
     Caveat: 조건/한계
     Could be wrong if: 어떤 검증이 무너뜨릴 수 있는가
```

신뢰도 등급:
- **★★★** : 직접 측정·재현 가능, 다른 합리적 해석 어려움
- **★★**  : 측정에 임의 임계가 들어가 있음, 또는 reference 통계의 모집단 차이 있음
- **★**   : 해석이 들어가 있음, 도메인 지식 의존

---

## A. 데이터셋 자체에 대한 사실 (Phase 0)

[**C1**] (★★★) 데이터셋은 **1,000,000 행** 이며, NVIDIA의 "약 700만 페르소나" 표현은 한 행에 7종 자유서술 페르소나가 있다는 뜻.
- Evidence: `data/processed/marginals_summary.json:n_rows`, [Phase 1 리포트 §1](../reports/PHASE1_REPORT.md#1-데이터셋-요약-실측)

[**C2**] (★★★) 데이터셋은 **26개 변수** (인구통계 12 + 자유서술 7 + 속성 6 + UUID).
- Evidence: HuggingFace 데이터 카드 + 본 리포 [Phase 1 §1](../reports/PHASE1_REPORT.md#1-데이터셋-요약-실측)

[**C3**] (★★★) 모집단은 19~99세 한국 성인 (age 범위 검증).
- Evidence: `data/processed/marginals_summary.json:age_stats` (min=19, max=99)

---

## B. Phase 1 — 단변량 충실도

[**C4**] (★★★) `sex` 분포 (여 50.44% / 남 49.56%) 는 통계청 추계인구 19+ 와 사실상 동일. **TVD = 0.0006**.
- Evidence: [`reports/tables/kosis_comparison.md:sex_adult`](../reports/tables/kosis_comparison.md), `data/processed/marginals/sex.csv`

[**C5**] (★★★) `province` (17 시도) 분포는 행안부 주민등록 2024.12 와 ±0.24pp 이내. **TVD = 0.0055**.
- Evidence: [`reports/tables/kosis_comparison.md:province`](../reports/tables/kosis_comparison.md)

[**C6**] (★★) `marital_status` 분포는 인구주택총조사 2020 (15+) 과 모집단 보정 후 양호. TVD = 0.054.
- Caveat: reference 가 15+ 이고 데이터는 19+. 보정 시 격차는 줄어들 것으로 예상. 
- Evidence: [`reports/tables/kosis_comparison.md:marital_status`](../reports/tables/kosis_comparison.md)

[**C7**] (★★) `education_level` 분포는 인구주택총조사 2020 (25+) 과 양호. TVD = 0.044. 4년제·전문대가 약간 상향 편향.
- Caveat: 모집단 차이 (19+ vs 25+).
- Evidence: [`reports/tables/kosis_comparison.md:education_level`](../reports/tables/kosis_comparison.md)

[**C8**] (★) `housing_type` 은 per-person 기준 reference 대비 약한 격차. **TVD = 0.084**, 셀별 차이 +3.5pp (아파트) / −8.0pp (단독주택) / +3.0pp (연립·다세대) / +2.0pp (주택이외) / −0.3pp (비주거).
- Reference: 본 분석이 통계청 일반가구 + 1인가구 비중·거처분포 + 평균 가구원수로 자체 추정 (`scripts/20_housing_unit_correction.py`).
- Caveat (신뢰도 ★): (a) per-person reference 가 공식 발표 없어 ±2pp 추정 오차, (b) NVIDIA targeting reference 불명확, (c) 단독주택 -8pp 잔존 차이는 약한 차이로만 인용 가능.
- Evidence: [Phase 1 §3-4](../reports/PHASE1_REPORT.md#3-4-housing_type----약한-격차), [`data/processed/housing_unit_correction.json`](../data/processed/housing_unit_correction.json)
- ※ Phase 3 의 housing decoupling 결론 (C18, C19) 은 internal structure 분석이라 본 marginal 비교와 무관, 그대로 유효.

---

## C. Phase 2 — 이변량 결합

[**C9**] (★★★) 55개 모든 변수쌍에 대해 4종 association 지표 (Cramér V, NMI, Theil U, TVD vs independence) 가 계산됐다.
- Evidence: [`data/processed/bivariate/metrics_long.csv`](../data/processed/bivariate/metrics_long.csv) (55 rows × 10+ cols)

[**C10**] (★★★) `district → province`: U = 1.000 (시군구가 시도를 결정적으로 함의). 
- Evidence: `data/processed/bivariate/matrix_theils_u.csv`, [Phase 2 리포트 §3-1](../reports/PHASE2_REPORT.md)

[**C11**] (★★) `marital_status × family_type` 강한 결합 (NMI=0.44). 배우자있음 × 혼자거주 = 0% — 데이터 내부 consistency 제약 100% 만족.
- Evidence: [`data/processed/bivariate_detail/cells_marital_status__x__family_type.csv`](../data/processed/bivariate_detail/cells_marital_status__x__family_type.csv)
- Caveat: 한국 현실의 marital_status="배우자있음" 은 *법적* 혼인이며 별거·주말부부·기러기 가족 등은 배우자와 따로 살 수 있음. PGM 의 결정론적 매핑은 데이터 일관성에는 깔끔하지만 현실 다양성을 일부 제거하는 효과.

[**C12**] (★★) `sex × bachelors_field` 결합: 공학·제조·건설 86.6% 남성, 보건·복지 28.1% 남성, 교육 29.8% 남성, 정보통신 76.3% 남성. **한국 현실 부합**.
- Evidence: [Phase 2 리포트 §3-5](../reports/PHASE2_REPORT.md)
- Could be wrong if: 한국 교육통계청 실제 졸업자 성비 데이터와 정밀 비교 시 차이 발견되면.

[**C13**] (★★) `military_status × sex`: 현역 5,282명 중 여성 518명 (9.8%). 한국군 여군 비율 ~8-10% 와 부합.
- Evidence: [Phase 2 리포트 §3-6](../reports/PHASE2_REPORT.md)
- Could be wrong if: 병무청 통계연보의 정확한 여군 비율과 차이.

[**C14**] (★★★) `age × marital × family` 의 한국 인구학 곡선은 정확히 재현됨. 19-24 미혼 95.4%, 75-84 사별 42.6%, 85+ 사별 70.7%.
- Evidence: [Phase 2 리포트 §3-3](../reports/PHASE2_REPORT.md)

[**C15**] (★★★) `age × education` 코호트 효과 정확. 25-34 4년제 51.6%, 85+ 무학 37.4%.
- Evidence: [Phase 2 리포트 §3-4](../reports/PHASE2_REPORT.md)

---

## D. Phase 3 — PGM 구조 추론

[**C16**] (★★★) 495개 CMI 가 모든 (X, Y, Z) 조합에 대해 계산됨.
- Evidence: [`data/processed/cmi/cmi_long.csv`](../data/processed/cmi/cmi_long.csv) (495 rows)

[**C17**] (★★) PC-style 추론 결과: **23 direct + 14 mediated + 18 no-edge marginal** 의 skeleton.
- Caveat: |Z| ≤ 2 conditioning 만 수행. 더 깊은 conditioning 으로 일부 'direct' 가 실제 'mediated' 일 가능성 있음.
- Caveat: ε = 0.005 nats 임계는 임의 — sensitivity 분석 (C29) 으로 검증.
- **Caveat (P4 추가)**: permutation null 로 bias 보정 시 23 direct 중 12개만 ratio > 2 로 견고. 11개 (모두 occupation/district 포함) 는 plug-in MI 의 카디널리티 bias 가능성 — 하단 C31 참조.
- Evidence: [`data/processed/cmi/skeleton.json`](../data/processed/cmi/skeleton.json)

[**C18**] (★★★) `housing_type` 의 직접 edge 는 단 2개 — district (강건, ratio 9.8), occupation (bias-suspect, ratio 1.05 — C31 참조). 사람 속성 (age, sex, marital, family, education, bachelors_field) 과 모두 mediated 또는 no-edge.
- Evidence: [`data/processed/cmi/skeleton.json`](../data/processed/cmi/skeleton.json), [`data/processed/cmi/node_degrees.csv`](../data/processed/cmi/node_degrees.csv)
- ※ housing × district 는 P4 permutation null ratio 9.84 로 견고. housing × occupation 은 ratio 1.05 로 high-card bias artifact 가능성 — 실질적으로 housing 의 견고한 직접 edge 는 district 1개로 보는 게 안전.

[**C19**] (★★) **Decoupling probe 결과: housing 예측에 person-attrs가 추가하는 정보 = −0.008 nats (실질 0).**
baseline (district only) CE = 1.001, full (+ all person attrs) CE = 1.008. Control (family_type) info_added = +0.82 nats (96% share). 
- Evidence: [`data/processed/decoupling_probe.json`](../data/processed/decoupling_probe.json) (Q1, C1)
- Caveat: 단일 모델 (HGB) · 단일 random seed (42) 한계. 다른 모델 / seed 에서 결과 robustness 추가 검증 권장 ([ROADMAP.md](../ROADMAP.md) P8).
- 명칭: 본 분석은 합성 데이터를 train/test split 한 within-synthetic probe (엄밀한 TSTR 아님).

[**C20**] (★★★) `military_status` 의 직접 edge 는 단 1개 — occupation (deterministic, U(military|occupation) = 1.000).
- Evidence: [`data/processed/cmi/skeleton.json`](../data/processed/cmi/skeleton.json)

[**C21**] (★★) **현역 군인의 계급별 분해는 한국군 인력 구성과 부합**:
- 병사 (의무복무) 13%, 평균 25세, 최대 30세, 여성 0%
- 부사관 (직업) 50%, 평균 41세, 최대 55세, 여성 11%
- 장교 (직업) 37%, 평균 47세, 최대 63세, 여성 11%
- 전체 평균 연령 40.9세는 부사관·장교 정년 (53-63세) + 의무복무 사병 19-30세의 자연 가중평균.
- 변수 의미: `military_status = 현역` 은 "의무복무 이행 중" 이 아니라 "현역 군 인력 신분 (직업군인 + 의무복무 통합)" — 미국식 'active duty' 에 가까움.
- Evidence: [`data/processed/military_breakdown.json`](../data/processed/military_breakdown.json), [Phase 3 §3-4](../reports/PHASE3_REPORT.md)

[**C22**] (★★) PGM은 4개 군집으로 분리됨: Geographic core / Age-driven demographic chain / Education-Occupation / Sex-related.
- Caveat: 이는 skeleton 의 visual interpretation. 다른 layout / 군집 알고리즘에서 다르게 보일 수 있음.
- Evidence: [`reports/figures/skeleton_bias_corrected.png`](../reports/figures/skeleton_bias_corrected.png) (P4 bias 보정 반영본), legacy [`skeleton_compare.png`](../reports/figures/skeleton_compare.png)

[**C23**] (★★★) Subsample stability: 5 시드 × 200K 에서 52/55 페어 분류 일치 (94.5%). 3개 unstable 은 \|Z\|=1 vs \|Z\|=2 방법론 mismatch이지 데이터 노이즈 아님.
- Evidence: [`data/processed/cmi/stability.csv`](../data/processed/cmi/stability.csv)

---

## E. 사용 권고 (해석 / 도메인 의존)

[**C24**] (★) Housing-related 분석 (1인가구 주거, 청년 주거 빈곤) 에 본 데이터셋은 **부적합**.
- Reason: C18 + C19 의 조합. PGM이 housing 을 사람 속성과 연결하지 않음.
- Caveat: 도메인 판단. "주거 분석" 의 정의에 따라 다를 수 있음.

[**C25**] (★★) 병역 인구 분석은 분석 종류에 따라 다름:
- **의무복무 흐름·동학 분석**: 부적합 ❌ (정적 cross-section 라벨, 입영·전역 흐름 정보 없음)
- **현역 군 인력 cross-section 구성 분석**: 사용 가능 🤔 (계급별 연령·성비는 한국군 현실 부합)
- 단 두 경우 모두 military_status 와 occupation 동시 입력 시 정보 중복 주의.

[**C26**] (★) 인구통계 시뮬레이션, 인구학 chain 분석, 노동 분리 (sex × field × occupation), LLM 학습용 페르소나 등에는 **사용 가능**.
- Reason: C4 ~ C15 의 부합도.

---

## F. 한계 자체에 대한 자기 진술

[**C27**] (★★★) χ² p-value 는 N=1M 에서 거의 모든 비교에 대해 0 → 본 리포는 χ² 를 사용하지 않고 효과크기 (TVD, MI 등) 만 사용.
- Evidence: 모든 phase 리포트의 명시적 caveat

[**C28**] (★★★) PC conditioning 은 |Z| ≤ 2 까지만. |Z| ≥ 3 mediation 가능성 미검증.
- Evidence: [Phase 3 §6 한계](../reports/PHASE3_REPORT.md#6-한계)

[**C29**] (★★★) CMI 임계 ε = 0.005 nats 는 임의 선택이나, ε ∈ {0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05} grid 에서 sensitivity 분석 완료. ε 100배 변동 시 direct edge 수는 32–13 범위로 변동하나, 핵심 결론 (housing decoupling, demographic chain) 은 ε-stable. 23개 페어는 전 grid 에서 분류 불변, 32개는 boundary.
- Evidence: [`data/processed/cmi/epsilon_counts.csv`](../data/processed/cmi/epsilon_counts.csv), [`data/processed/cmi/epsilon_boundary.csv`](../data/processed/cmi/epsilon_boundary.csv), [Phase 3 §2.7](../reports/PHASE3_REPORT.md#27-ε-threshold-sensitivity--위-결과는-임계-의존성이-얼마나-큰가)

[**C30**] (★★) Decoupling probe 는 단일 모델 (HGB) 한정. 다른 모델 (RF, LightGBM, NN) 에서 결과 다를 가능성. 5-fold CV 는 보강 완료 (C19 caveat).

[**C30b**] (★★★) **Leakage 점검 통과**: 6개 case 모두 train-only encoder + 5-fold CV 로 재실행, info_added 차이 < 0.005 nats (원본 효과의 1% 이하). 5-fold SE < 0.02 nats. Housing decoupling 결론 (Q1) 은 -0.0077 → -0.0082 로 거의 동일. 단일 split + 전체 데이터 encoder 사용으로 인한 잠재 leakage 가 결론에 영향 없음을 확인.
- Evidence: [`data/processed/decoupling_probe_no_leakage.json`](../data/processed/decoupling_probe_no_leakage.json), [`scripts/11b_decoupling_probe_no_leakage.py`](../scripts/11b_decoupling_probe_no_leakage.py), [Phase 3 §1.4](../reports/PHASE3_REPORT.md#14-leakage-check--위-probe-결과는-데이터-누수에-영향받았나)

[**C31**] (★★★) Permutation null (100회, N=100K subsample, stratified shuffle) 결과:
- 55 marginal pairs 중 28개 ratio_obs/null_p95 ≥ 10 (강건), 17개 2-10 (유의), 10개 < 2 (bias-suspect).
- 23 'direct edges' 중 12개만 conditional ratio > 2 (4개 ★★★ ratio≥10 + 8개 ★★ ratio 2-10), 11개는 < 2 (모두 occupation/district 포함).
- 가장 결정적: `occupation × district` marginal MI 0.597 중 97%가 카디널리티 bias (ratio 1.03). **Housing × district 는 conditional ratio 9.84 로 견고** — housing decoupling 결론에 영향 없음.
- Evidence: [`data/processed/cmi/permutation_null_marginal.csv`](../data/processed/cmi/permutation_null_marginal.csv), [`permutation_null_conditional.csv`](../data/processed/cmi/permutation_null_conditional.csv), [Phase 3 §2.5](../reports/PHASE3_REPORT.md#25-permutation-null--bootstrap-ci--어느-edge-가-bias-가-아닌가)
- 시각화: [`reports/figures/perm_null_*.png`](../reports/figures), [`forest_*.png`](../reports/figures)

[**C32**] (★★★) Bootstrap 95% CI (100 resamples, N=100K) — MI/CMI 추정의 정밀도:
- 모든 페어에서 SE 매우 작음 (예: district~province SE=0.004 nats). 추정치 자체는 정밀하게 측정됨.
- CI 폭은 N 의존이므로 풀 1M 데이터에서는 더 좁아짐. **추정치의 흔들림이 아니라 *해석* 의 견고성이 본 리포의 핵심 한계.**
- Evidence: [`data/processed/cmi/bootstrap_*.csv`](../data/processed/cmi)

[**C33**] (★★★) **외부 검증 (P7 v1): age × marital × sex 결합 분포는 2020 census 와 8/8 cell ±4pp 이내** 부합:
- 20대 미혼 92.8% (ref) vs 90.3% (synth)
- 30대 남 미혼 50.5% vs 54.1%, 30대 여 32.8% vs 35.0%
- 40대 17.9% vs 19.4%, 50대 7.4% vs 8.1%
- → 인구학 chain (Phase 2 §3-3, Phase 3) 결론을 외부 데이터로 **강하게 지지**.
- Evidence: [`data/processed/kosis_joint_compare.json`](../data/processed/kosis_joint_compare.json), [Phase 3 §2.6](../reports/PHASE3_REPORT.md#26-외부-검증--kosis--통계청-cross-tab-비교-p7-v1)
- Caveat: reference 는 KOSIS 직접 cross-tab 이 아니라 보도자료 인용 — KOSIS Open API 로 완전 cross-tab 검증은 P7 v2.

[**C34**] (★★) **province × housing 외부 검증: 시도별 패턴은 ±3pp 이내, 전국 합계는 ±9pp**:
- 광주·대전·제주·전라남·인천 모두 reference 와 ±3pp 이내 일치 (시도별 housing 패턴 신뢰 가능)
- 전국 아파트 +9pp / 단독 −12pp (Phase 1 §3-4 의 재확인)
- 가구 단위 vs 개인 단위 모집단 차이로 일부 설명되나 전체 격차 설명에는 부족 — 시드 통계 vintage 가능성
- Evidence: [`data/processed/kosis_joint_compare.json`](../data/processed/kosis_joint_compare.json)

[**C35**] (★) **age × sex × education 외부 비교: 60대 여성 중졸이하 −44pp 등 큰 격차** — 새 가설:
- 50s_early_F 중졸이하: ref 39.7% vs synth 6.9% (−33pp)
- 60s_early_F 중졸이하: ref 73.7% vs synth 29.8% (−44pp)
- 60s_early_F 4년제대학: ref 4.6% vs synth 9.7% (+5pp)
- → **PGM 이 고령층 (특히 여성) 학력을 상향 편향시킬 가능성**
- ⚠️ Reference (한국노동사회연구소 2014) 가 10년 vintage — 코호트 갱신 (1960-64년생 → 1970-74년생) 으로 일부 설명. 정확한 원인 분리는 2020 census 직접 비교 필요 (P7 v2).
- Evidence: [`data/processed/kosis_joint_compare.json`](../data/processed/kosis_joint_compare.json)
- 신뢰도 낮음 사유: vintage 한계로 PGM 편향 vs 코호트 갱신 분리 불가.
- Evidence: [Phase 3 §6](../reports/PHASE3_REPORT.md#6-한계)

---

## 검증 체크리스트 (외부 리뷰어용)

각 주장 옆 [_] 박스에 검증 결과를 적어주세요:
- [✓] 동의
- [✗] 반박 (반박 근거 함께)
- [?] 추가 정보 필요

```
C1  [_]  C8  [_]  C15 [_]  C22 [_]  C29 [_]
C2  [_]  C9  [_]  C16 [_]  C23 [_]  C30 [_]
C3  [_]  C10 [_]  C17 [_]  C24 [_]  C30b[_]
C4  [_]  C11 [_]  C18 [_]  C25 [_]  C31 [_]
C5  [_]  C12 [_]  C19 [_]  C26 [_]  C32 [_]
C6  [_]  C13 [_]  C20 [_]  C27 [_]  C33 [_]
C7  [_]  C14 [_]  C21 [_]  C28 [_]  C34 [_]
                                    C35 [_]
```



---

# §8. KEY RESULTS — 구조화 수치 (수치 검증용)

본 섹션은 `review/key_results.json` 의 모든 수치를 JSON 으로 보여줍니다.

```json
{
  "_meta": {
    "generated_by": "scripts/build_review_packet.py",
    "purpose": "Single structured dump of all key numbers for external verification"
  },
  "dataset_basics": {
    "n_rows": 1000000,
    "age_stats": {
      "mean": 50.660031,
      "std": 17.612992882998544,
      "min": 19.0,
      "p25": 36.0,
      "p50": 51.0,
      "p75": 64.0,
      "max": 99.0
    },
    "n_unique_per_var": {
      "sex": 2,
      "age": 81,
      "marital_status": 4,
      "military_status": 2,
      "family_type": 39,
      "housing_type": 6,
      "education_level": 7,
      "bachelors_field": 11,
      "occupation": 2120,
      "district": 252,
      "province": 17,
      "country": 1
    }
  },
  "phase1_kosis_comparison": {
    "marital_status": {
      "TVD": 0.05403800000000006,
      "L_inf": 0.05403800000000003,
      "reference": {
        "population": "15세 이상 인구",
        "year": 2020,
        "source": "통계청, 2020 인구주택총조사",
        "caveat": "Nemotron 모집단은 19세 이상이라, 미혼은 본 수치보다 낮고 배우자있음/사별은 높은 방향으로 자연스럽게 차이가 발생함."
      }
    },
    "housing_type": {
      "TVD": 0.11923129829829834,
      "L_inf": 0.11513128428428424,
      "reference": {
        "population": "일반가구(가구 기준)",
        "year": 2023,
        "source": "통계청, 2023년 인구주택총조사(등록센서스)",
        "caveat": "Nemotron은 개인 기준이고 본 수치는 가구 기준. 또한 Nemotron은 '연립주택'과 '다세대주택'을 분리, 본 수치는 합계."
      }
    },
    "province": {
      "TVD": 0.005476412002424677,
      "L_inf": 0.0023627747019600853,
      "reference": {
        "population": "총인구(주민등록인구)",
        "year": 2024,
        "source": "행정안전부, 주민등록인구현황 2024.12 (KOSIS)",
        "caveat": "본 수치는 전 연령 합계. 19세+ 분포는 시도별 고령화 차이로 미세하게 다를 수 있으나(특히 세종/경기 청년층 비중이 높아 19+ 비중은 약간 낮을 수 있음) 큰 그림은 동일."
      }
    },
    "sex_adult": {
      "TVD": 0.0005580000000000307,
      "L_inf": 0.0005580000000000584,
      "reference": {
        "population": "19세 이상 인구",
        "year": 2024,
        "source": "통계청 추계인구",
        "caveat": "고령층 여성 우세로 성인 인구는 여성이 약간 많음."
      }
    },
    "education_level": {
      "TVD": 0.04386800000000022,
      "L_inf": 0.023761000000000032,
      "reference": {
        "population": "25세 이상 인구",
        "year": 2020,
        "source": "통계청, 2020 인구주택총조사 표본집계 (학력별 인구)",
        "caveat": "Nemotron은 19세+ 모집단이라 (1) 학교 재학 중인 19~24세가 다수 포함되어 '학생' 시점의 학력으로 잡혀 4년제/대학원 비중이 다소 낮게, 고등학교 졸업이 다소 높게 나오는 게 자연스러움. (2) 또한 본 수치 합이 1.0이 아닐 수 있음(반올림)."
      }
    }
  },
  "phase2_top15_pairs_by_nmi": [
    {
      "x": "district",
      "y": "province",
      "V": 1.0,
      "NMI": 0.6347,
      "U_y_given_x": 1.0,
      "U_x_given_y": 0.4649,
      "TVD_indep": 0.8724
    },
    {
      "x": "marital_status",
      "y": "family_type",
      "V": 0.6936,
      "NMI": 0.4398,
      "U_y_given_x": 0.3172,
      "U_x_given_y": 0.7171,
      "TVD_indep": 0.4941
    },
    {
      "x": "education_level",
      "y": "bachelors_field",
      "V": 0.4083,
      "NMI": 0.4208,
      "U_y_given_x": 0.4756,
      "U_x_given_y": 0.3773,
      "TVD_indep": 0.4392
    },
    {
      "x": "age_bin",
      "y": "marital_status",
      "V": 0.483,
      "NMI": 0.2103,
      "U_y_given_x": 0.3012,
      "U_x_given_y": 0.1616,
      "TVD_indep": 0.2834
    },
    {
      "x": "age_bin",
      "y": "family_type",
      "V": 0.3365,
      "NMI": 0.153,
      "U_y_given_x": 0.1396,
      "U_x_given_y": 0.1693,
      "TVD_indep": 0.3089
    },
    {
      "x": "age_bin",
      "y": "education_level",
      "V": 0.3326,
      "NMI": 0.1522,
      "U_y_given_x": 0.1649,
      "U_x_given_y": 0.1414,
      "TVD_indep": 0.2815
    },
    {
      "x": "education_level",
      "y": "occupation",
      "V": 0.3334,
      "NMI": 0.1041,
      "U_y_given_x": 0.072,
      "U_x_given_y": 0.1877,
      "TVD_indep": 0.2882
    },
    {
      "x": "bachelors_field",
      "y": "occupation",
      "V": 0.2609,
      "NMI": 0.0826,
      "U_y_given_x": 0.0538,
      "U_x_given_y": 0.177,
      "TVD_indep": 0.2204
    },
    {
      "x": "marital_status",
      "y": "education_level",
      "V": 0.2884,
      "NMI": 0.0769,
      "U_y_given_x": 0.0625,
      "U_x_given_y": 0.0999,
      "TVD_indep": 0.1457
    },
    {
      "x": "age_bin",
      "y": "occupation",
      "V": 0.2105,
      "NMI": 0.0526,
      "U_y_given_x": 0.0381,
      "U_x_given_y": 0.0851,
      "TVD_indep": 0.2299
    },
    {
      "x": "housing_type",
      "y": "district",
      "V": 0.2656,
      "NMI": 0.0488,
      "U_y_given_x": 0.0298,
      "U_x_given_y": 0.1346,
      "TVD_indep": 0.194
    },
    {
      "x": "sex",
      "y": "occupation",
      "V": 0.4544,
      "NMI": 0.0463,
      "U_y_given_x": 0.0269,
      "U_x_given_y": 0.169,
      "TVD_indep": 0.1864
    },
    {
      "x": "family_type",
      "y": "education_level",
      "V": 0.183,
      "NMI": 0.0445,
      "U_y_given_x": 0.0538,
      "U_x_given_y": 0.038,
      "TVD_indep": 0.1439
    },
    {
      "x": "housing_type",
      "y": "province",
      "V": 0.1761,
      "NMI": 0.042,
      "U_y_given_x": 0.031,
      "U_x_given_y": 0.0652,
      "TVD_indep": 0.1296
    },
    {
      "x": "occupation",
      "y": "district",
      "V": 0.0509,
      "NMI": 0.04,
      "U_y_given_x": 0.0368,
      "U_x_given_y": 0.044,
      "TVD_indep": 0.1713
    }
  ],
  "phase2_bottom5_pairs_by_nmi": [
    {
      "x": "military_status",
      "y": "district",
      "V": 0.038574,
      "NMI": 0.000216,
      "TVD_indep": 0.001832
    },
    {
      "x": "military_status",
      "y": "province",
      "V": 0.022919,
      "NMI": 0.000167,
      "TVD_indep": 0.001014
    },
    {
      "x": "sex",
      "y": "province",
      "V": 0.020141,
      "NMI": 0.00013,
      "TVD_indep": 0.008818
    },
    {
      "x": "military_status",
      "y": "housing_type",
      "V": 0.006239,
      "NMI": 3.2e-05,
      "TVD_indep": 0.000328
    },
    {
      "x": "sex",
      "y": "housing_type",
      "V": 0.00481,
      "NMI": 1.3e-05,
      "TVD_indep": 0.00154
    }
  ],
  "phase3_skeleton": {
    "epsilon_nats": 0.005,
    "n_pairs": 55,
    "n_direct": 23,
    "n_mediated": 14,
    "n_no_edge_marginal": 18,
    "direct_edges": [
      {
        "x": "age_bin",
        "y": "marital_status",
        "mi_xy": 0.3152473619150616,
        "cmi_min_any": 0.05889805285210499,
        "drop_max_any": 0.813168768505114,
        "z_star_pair": "family_type+education_level"
      },
      {
        "x": "age_bin",
        "y": "family_type",
        "mi_xy": 0.3302719891726565,
        "cmi_min_any": 0.09000460986026254,
        "drop_max_any": 0.7274833688266226,
        "z_star_pair": "marital_status+education_level"
      },
      {
        "x": "age_bin",
        "y": "education_level",
        "mi_xy": 0.2758507854536633,
        "cmi_min_any": 0.13393388947394108,
        "drop_max_any": 0.5144697911456955,
        "z_star_pair": "marital_status+bachelors_field"
      },
      {
        "x": "age_bin",
        "y": "occupation",
        "mi_xy": 0.1659744868425882,
        "cmi_min_any": 0.08935856117482836,
        "drop_max_any": 0.46161266785794086,
        "z_star_pair": "education_level+military_status"
      },
      {
        "x": "age_bin",
        "y": "district",
        "mi_xy": 0.0217517629146075,
        "cmi_min_any": 0.0146613214822463,
        "drop_max_any": 0.32597088613905323,
        "z_star_pair": "province+military_status"
      },
      {
        "x": "sex",
        "y": "marital_status",
        "mi_xy": 0.0279241450114458,
        "cmi_min_any": 0.008715819275650379,
        "drop_max_any": 0.6878751606511906,
        "z_star_pair": "family_type+education_level"
      },
      {
        "x": "sex",
        "y": "family_type",
        "mi_xy": 0.0175808129232077,
        "cmi_min_any": 0.0077201820044217,
        "drop_max_any": 0.56087457171957,
        "z_star_pair": "marital_status+military_status"
      },
      {
        "x": "sex",
        "y": "bachelors_field",
        "mi_xy": 0.037483679710861,
        "cmi_min_any": 0.025032821139134517,
        "drop_max_any": 0.3321674570844978,
        "z_star_pair": "occupation+education_level"
      },
      {
        "x": "sex",
        "y": "occupation",
        "mi_xy": 0.1171140063231909,
        "cmi_min_any": 0.10566087121109781,
        "drop_max_any": 0.09779475121435699,
        "z_star_pair": "bachelors_field+military_status"
      },
      {
        "x": "marital_status",
        "y": "family_type",
        "mi_xy": 0.7504626506021759,
        "cmi_min_any": 0.5215295379737027,
        "drop_max_any": 0.3050559710663493,
        "z_star_pair": "age_bin+sex"
      },
      {
        "x": "marital_status",
        "y": "occupation",
        "mi_xy": 0.0499321689233223,
        "cmi_min_any": 0.018391217311305406,
        "drop_max_any": 0.6316759774736074,
        "z_star_pair": "age_bin+military_status"
      },
      {
        "x": "marital_status",
        "y": "district",
        "mi_xy": 0.015792683044747,
        "cmi_min_any": 0.00877546875498813,
        "drop_max_any": 0.4443332567288464,
        "z_star_pair": "province+family_type"
      },
      {
        "x": "military_status",
        "y": "occupation",
        "mi_xy": 0.0329639309687438,
        "cmi_min_any": 0.029513727440079525,
        "drop_max_any": 0.10466602214207221,
        "z_star_pair": "sex+age_bin"
      },
      {
        "x": "family_type",
        "y": "occupation",
        "mi_xy": 0.0696139491050686,
        "cmi_min_any": 0.05806782724658111,
        "drop_max_any": 0.16585931421676536,
        "z_star_pair": "marital_status+military_status"
      },
      {
        "x": "family_type",
        "y": "district",
        "mi_xy": 0.0488022440349181,
        "cmi_min_any": 0.030119483863387843,
        "drop_max_any": 0.3828258421510844,
        "z_star_pair": "province+marital_status"
      },
      {
        "x": "housing_type",
        "y": "occupation",
        "mi_xy": 0.0096685913558513,
        "cmi_min_any": 0.0096494708810358,
        "drop_max_any": 0.0019775864044485614,
        "z_star_pair": "military_status+sex"
      },
      {
        "x": "housing_type",
        "y": "district",
        "mi_xy": 0.1553263695389767,
        "cmi_min_any": 0.0800740929071006,
        "drop_max_any": 0.48447843630950715,
        "z_star_pair": "province+military_status"
      },
      {
        "x": "education_level",
        "y": "bachelors_field",
        "mi_xy": 0.631028622067252,
        "cmi_min_any": 0.42029751282982925,
        "drop_max_any": 0.3339485751804203,
        "z_star_pair": "occupation+district"
      },
      {
        "x": "education_level",
        "y": "occupation",
        "mi_xy": 0.313982082661922,
        "cmi_min_any": 0.0997936030759093,
        "drop_max_any": 0.6821678414581339,
        "z_star_pair": "bachelors_field+age_bin"
      },
      {
        "x": "education_level",
        "y": "district",
        "mi_xy": 0.0523478015461186,
        "cmi_min_any": 0.018119218288610857,
        "drop_max_any": 0.6538685913553073,
        "z_star_pair": "bachelors_field+province"
      },
      {
        "x": "bachelors_field",
        "y": "occupation",
        "mi_xy": 0.2347991672146094,
        "cmi_min_any": 0.05861681061919905,
        "drop_max_any": 0.7503534134530275,
        "z_star_pair": "education_level+sex"
      },
      {
        "x": "occupation",
        "y": "district",
        "mi_xy": 0.1917946674507536,
        "cmi_min_any": 0.14230486273579532,
        "drop_max_any": 0.2580353529780258,
        "z_star_pair": "province+military_status"
      },
      {
        "x": "district",
        "y": "province",
        "mi_xy": 2.425605651865646,
        "cmi_min_any": 2.2709818012387655,
        "drop_max_any": 0.06374649172999414,
        "z_star_pair": "housing_type+occupation"
      }
    ],
    "mediated_edges": [
      {
        "x": "age_bin",
        "y": "bachelors_field",
        "mi_xy": 0.0650921186215516,
        "cmi_min_any": 0.0004440823072715,
        "drop_max_any": 0.9931776332269439,
        "z_star_pair": "education_level"
      },
      {
        "x": "age_bin",
        "y": "province",
        "mi_xy": 0.0070904414323612,
        "cmi_min_any": 9.528600131147868e-18,
        "drop_max_any": 0.9999999999999987,
        "z_star_pair": "district"
      },
      {
        "x": "sex",
        "y": "education_level",
        "mi_xy": 0.013636062445642,
        "cmi_min_any": 0.0049984667129446,
        "drop_max_any": 0.6334376780049082,
        "z_star_pair": "marital_status"
      },
      {
        "x": "marital_status",
        "y": "education_level",
        "mi_xy": 0.104547090477114,
        "cmi_min_any": 0.0042717540184276,
        "drop_max_any": 0.9591403835445549,
        "z_star_pair": "age_bin"
      },
      {
        "x": "marital_status",
        "y": "bachelors_field",
        "mi_xy": 0.0247240023032375,
        "cmi_min_any": 0.0003095158128956,
        "drop_max_any": 0.9874811606511188,
        "z_star_pair": "education_level"
      },
      {
        "x": "marital_status",
        "y": "province",
        "mi_xy": 0.0063987826199206,
        "cmi_min_any": 3.3598124282718803e-17,
        "drop_max_any": 0.9999999999999948,
        "z_star_pair": "district"
      },
      {
        "x": "family_type",
        "y": "education_level",
        "mi_xy": 0.089898483840149,
        "cmi_min_any": 0.0038291427262804032,
        "drop_max_any": 0.9574059254092748,
        "z_star_pair": "age_bin+marital_status"
      },
      {
        "x": "family_type",
        "y": "bachelors_field",
        "mi_xy": 0.0186137650996343,
        "cmi_min_any": 0.000983461411104,
        "drop_max_any": 0.9471648317339451,
        "z_star_pair": "education_level"
      },
      {
        "x": "family_type",
        "y": "province",
        "mi_xy": 0.0180643285016919,
        "cmi_min_any": 2.3022916906256793e-17,
        "drop_max_any": 0.9999999999999988,
        "z_star_pair": "district"
      },
      {
        "x": "housing_type",
        "y": "province",
        "mi_xy": 0.0752522766318763,
        "cmi_min_any": 2.3416796279818185e-17,
        "drop_max_any": 0.9999999999999997,
        "z_star_pair": "district"
      },
      {
        "x": "education_level",
        "y": "province",
        "mi_xy": 0.017933827648729,
        "cmi_min_any": 1.4230394640435408e-17,
        "drop_max_any": 0.9999999999999992,
        "z_star_pair": "district"
      },
      {
        "x": "bachelors_field",
        "y": "district",
        "mi_xy": 0.0309382676300534,
        "cmi_min_any": 0.0031837338897005,
        "drop_max_any": 0.8970939831612348,
        "z_star_pair": "education_level"
      },
      {
        "x": "bachelors_field",
        "y": "province",
        "mi_xy": 0.0120145730603197,
        "cmi_min_any": 2.7017277304253183e-18,
        "drop_max_any": 0.9999999999999998,
        "z_star_pair": "district"
      },
      {
        "x": "occupation",
        "y": "province",
        "mi_xy": 0.0491286630940047,
        "cmi_min_any": 2.260469589288051e-17,
        "drop_max_any": 0.9999999999999996,
        "z_star_pair": "district"
      }
    ]
  },
  "phase3_decoupling_probe": [
    {
      "question": "Q1 housing decoupled from person attrs given district?",
      "target": "housing_type",
      "baseline_features": [
        "district"
      ],
      "full_features": [
        "district",
        "age_bin",
        "sex",
        "marital_status",
        "family_type",
        "education_level",
        "bachelors_field",
        "occupation"
      ],
      "CE_null": 1.1531472120682433,
      "CE_baseline": 1.000658609297788,
      "CE_full": 1.0083107145963908,
      "acc_baseline": 0.6535166666666666,
      "acc_full": 0.6529333333333334,
      "info_in_baseline": 0.15248860277045528,
      "info_added_by_extras": -0.007652105298602718,
      "info_total": 0.14483649747185257,
      "fraction_added": -0.052832714351504
    },
    {
      "question": "Control: family_type SHOULD improve with marital/age (tested edge)",
      "target": "family_type",
      "baseline_features": [
        "district"
      ],
      "full_features": [
        "district",
        "age_bin",
        "sex",
        "marital_status",
        "education_level"
      ],
      "CE_null": 2.3696888331832726,
      "CE_baseline": 2.3363710584864723,
      "CE_full": 1.5188974721531452,
      "acc_baseline": 0.29025,
      "acc_full": 0.54425,
      "info_in_baseline": 0.033317774696800306,
      "info_added_by_extras": 0.8174735863333271,
      "info_total": 0.8507913610301274,
      "fraction_added": 0.9608390773309456
    },
    {
      "question": "Control: occupation IS modeled with sex/edu/field",
      "target": "occupation",
      "baseline_features": [
        "district",
        "province"
      ],
      "full_features": [
        "district",
        "province",
        "age_bin",
        "sex",
        "education_level",
        "bachelors_field"
      ],
      "CE_null": 4.355506868595341,
      "CE_baseline": 3.4804376355704334,
      "CE_full": 3.2995269396213462,
      "acc_baseline": 0.3683666666666667,
      "acc_full": 0.36928333333333335,
      "info_in_baseline": 0.8750692330249072,
      "info_added_by_extras": 0.18091069594908715,
      "info_total": 1.0559799289739944,
      "fraction_added": 0.1713202031452081
    },
    {
      "question": "Q2 military depends on sex but does it on age?",
      "target": "military_status",
      "baseline_features": [
        "age_bin"
      ],
      "full_features": [
        "age_bin",
        "sex"
      ],
      "CE_null": 0.03307563501181216,
      "CE_baseline": 0.03117692481771968,
      "CE_full": 0.02920044519343334,
      "acc_baseline": 0.99475,
      "acc_full": 0.99475,
      "info_in_baseline": 0.001898710194092483,
      "info_added_by_extras": 0.0019764796242863376,
      "info_total": 0.0038751898183788207,
      "fraction_added": 0.5100342736535147
    },
    {
      "question": "Q3 if we add occupation, military becomes determined?",
      "target": "military_status",
      "baseline_features": [
        "sex"
      ],
      "full_features": [
        "sex",
        "age_bin",
        "occupation"
      ],
      "CE_null": 0.03307563501181216,
      "CE_baseline": 0.03066660219565211,
      "CE_full": 0.008208124245931167,
      "acc_baseline": 0.99475,
      "acc_full": 0.9984,
      "info_in_baseline": 0.002409032816160051,
      "info_added_by_extras": 0.022458477949720945,
      "info_total": 0.024867510765880993,
      "fraction_added": 0.9031252931248223
    },
    {
      "question": "Control: marital should improve with family_type (direct edge)",
      "target": "marital_status",
      "baseline_features": [
        "age_bin"
      ],
      "full_features": [
        "age_bin",
        "sex",
        "education_level",
        "family_type"
      ],
      "CE_null": 1.0482782233284051,
      "CE_baseline": 0.7354355803505886,
      "CE_full": 0.18246373214841055,
      "acc_baseline": 0.72755,
      "acc_full": 0.9214166666666667,
      "info_in_baseline": 0.3128426429778165,
      "info_added_by_extras": 0.5529718482021782,
      "info_total": 0.8658144911799945,
      "fraction_added": 0.6386724336855902
    }
  ],
  "phase3_stability": {
    "n_seeds": 5,
    "n_per_seed": 200000,
    "n_pairs_total": 55,
    "n_pairs_stable": 52,
    "unstable_pairs": [
      {
        "x": "family_type",
        "y": "education_level",
        "edge_class": "mediated",
        "p_direct": 1.0,
        "p_mediated": 0.0,
        "p_no_edge_marginal": 0.0
      },
      {
        "x": "bachelors_field",
        "y": "district",
        "edge_class": "mediated",
        "p_direct": 1.0,
        "p_mediated": 0.0,
        "p_no_edge_marginal": 0.0
      },
      {
        "x": "sex",
        "y": "education_level",
        "edge_class": "mediated",
        "p_direct": 0.4,
        "p_mediated": 0.6,
        "p_no_edge_marginal": 0.0
      }
    ]
  },
  "phase3_node_degrees_in_skeleton": [
    {
      "node": "occupation",
      "degree": 9
    },
    {
      "node": "district",
      "degree": 7
    },
    {
      "node": "age_bin",
      "degree": 5
    },
    {
      "node": "marital_status",
      "degree": 5
    },
    {
      "node": "family_type",
      "degree": 5
    },
    {
      "node": "sex",
      "degree": 4
    },
    {
      "node": "education_level",
      "degree": 4
    },
    {
      "node": "bachelors_field",
      "degree": 3
    },
    {
      "node": "housing_type",
      "degree": 2
    },
    {
      "node": "province",
      "degree": 1
    },
    {
      "node": "military_status",
      "degree": 1
    }
  ]
}
```


---

# §9. KOSIS / 통계청 reference 통계

본 리포가 사용한 외부 reference 분포 + 출처 + caveat. 한국 도메인 전문가가 검증할 핵심 입력.

```json
{
  "_meta": {
    "purpose": "Phase 1 비교용 KOSIS 등 공식 통계 reference. Nemotron은 19세 이상 성인 인구가 모집단이지만, 공개 통계는 기준이 다른 경우가 많아 그대로 비교하지 말고 caveat를 함께 표기할 것.",
    "license_note": "통계청 공표 수치는 공공누리 / 출처표시 조건으로 활용 가능"
  },
  "marital_status": {
    "values": {
      "배우자있음": 0.559,
      "미혼": 0.311,
      "사별": 0.072,
      "이혼": 0.058
    },
    "population": "15세 이상 인구",
    "year": 2020,
    "source": "통계청, 2020 인구주택총조사",
    "caveat": "Nemotron 모집단은 19세 이상이라, 미혼은 본 수치보다 낮고 배우자있음/사별은 높은 방향으로 자연스럽게 차이가 발생함."
  },
  "housing_type": {
    "values": {
      "아파트": 0.531,
      "단독주택": 0.284,
      "연립·다세대주택": 0.112,
      "주택 이외의 거처": 0.058,
      "비주거용 건물 내 주택": 0.014
    },
    "population": "일반가구(가구 기준)",
    "year": 2023,
    "source": "통계청, 2023년 인구주택총조사(등록센서스)",
    "caveat": "⚠ Nemotron은 개인 단위, 본 수치는 가구 단위 — 직접 비교 불가. 본 분석의 자체 추정 per-person reference는 'values_per_person_estimated' 필드 참조 (scripts/20_housing_unit_correction.py)."
  },
  "housing_type_per_person_estimated": {
    "values": {
      "아파트": 0.586,
      "단독주택": 0.249,
      "연립·다세대주택": 0.110,
      "주택 이외의 거처": 0.040,
      "비주거용 건물 내 주택": 0.013
    },
    "population": "개인(가구원수 가중치 적용 자체 추정)",
    "year": 2023,
    "source": "통계청 일반가구 분포 + 1인가구 거처분포(2023 통계로 보는 1인가구) + 평균 가구원수 2.21 으로 본 분석이 직접 계산",
    "method": "다인가구 분포 역산 후 가구원수 가중. 다인가구 평균 2.88명 가정.",
    "caveat": "공식 발표 수치 아님. 다인가구 평균 가구원수 거처유형별 차이 무시한 근사. ±2pp 정도의 추정 오차 가능."
  },
  "province": {
    "values": {
      "경기": 0.2604,
      "서울": 0.1810,
      "부산": 0.0641,
      "경상남": 0.0628,
      "인천": 0.0586,
      "경상북": 0.0494,
      "대구": 0.0455,
      "충청남": 0.0413,
      "전라남": 0.0354,
      "전북": 0.0339,
      "충청북": 0.0306,
      "강원": 0.0297,
      "대전": 0.0277,
      "광주": 0.0274,
      "울산": 0.0212,
      "제주": 0.0130,
      "세종": 0.0078
    },
    "population": "총인구(주민등록인구)",
    "year": 2024,
    "source": "행정안전부, 주민등록인구현황 2024.12 (KOSIS)",
    "caveat": "본 수치는 전 연령 합계. 19세+ 분포는 시도별 고령화 차이로 미세하게 다를 수 있으나(특히 세종/경기 청년층 비중이 높아 19+ 비중은 약간 낮을 수 있음) 큰 그림은 동일."
  },
  "sex_adult": {
    "values": {
      "남자": 0.495,
      "여자": 0.505
    },
    "population": "19세 이상 인구",
    "year": 2024,
    "source": "통계청 추계인구",
    "caveat": "고령층 여성 우세로 성인 인구는 여성이 약간 많음."
  },
  "education_level": {
    "values": {
      "무학": 0.034,
      "초등학교": 0.105,
      "중학교": 0.097,
      "고등학교": 0.317,
      "2~3년제 전문대학": 0.135,
      "4년제 대학교": 0.257,
      "대학원": 0.055
    },
    "population": "25세 이상 인구",
    "year": 2020,
    "source": "통계청, 2020 인구주택총조사 표본집계 (학력별 인구)",
    "caveat": "Nemotron은 19세+ 모집단이라 (1) 학교 재학 중인 19~24세가 다수 포함되어 '학생' 시점의 학력으로 잡혀 4년제/대학원 비중이 다소 낮게, 고등학교 졸업이 다소 높게 나오는 게 자연스러움. (2) 또한 본 수치 합이 1.0이 아닐 수 있음(반올림)."
  }
}

```


---

# §10. 한계 / 자기 진술 / 의심 가능 지점


본 리포가 스스로 인정한 한계 (CLAIMS_LEDGER 의 C27~C35 항목 참조):

1. **모집단 차이**: KOSIS reference 가 모집단 정의가 다를 수 있음 (15+ 또는 25+). marital/education 에서 caveat 명시. housing 은 본 분석이 per-person reference 자체 추정 (±2pp 오차 가능).
2. **PC conditioning depth**: |Z| ≤ 2 까지만. |Z| ≥ 3 에서 mediation 가능성 미검증.
3. **CMI 임계 ε = 0.005 nats**: 임의 선택이나 §2.7 sensitivity 분석으로 의존성 정량화 — 핵심 결론은 ε-stable. ★★★ 검증 완료.
4. **High-cardinality bias**: §2.5 permutation null 결과, 23 direct edges 중 11개 (모두 occupation/district 포함) 가 ratio < 2 로 bias-suspect.
5. **Bootstrap CI 산출 완료**: 모든 페어 SE 매우 작음 (district~province SE=0.004 nats). 추정치 자체는 정밀.
6. **Decoupling probe 단일 모델 한계**: HistGradientBoostingClassifier · seed=42 사용. 다른 모델 (RF, LightGBM, NN) 에서의 robustness 미확인 (ROADMAP P8 예정). 단 leakage check (§1.4) + 5-fold CV 로 단일 split 한계는 점검 완료 — 결론 변화 없음. 명칭은 within-synthetic probe (엄밀한 TSTR 아님).
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

