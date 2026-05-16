# 방법론 종합

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

(용어 정의: [GLOSSARY](GLOSSARY.md#decoupling-probe-predictive-conditional-independence-probe) 참조)

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
