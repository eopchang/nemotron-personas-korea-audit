# 주장 원장 (Claims Ledger)

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

[**C8**] (★★) `housing_type` 은 인구주택총조사 2023 가구 기준과 **TVD = 0.119** 로 가장 큰 차이. 아파트 +8.9pp, 단독 −11.5pp.
- Caveat: 가구 vs 개인 모집단 차이로 일부 설명되나 격차의 폭을 충분히 메우지 못함.
- Evidence: [`reports/tables/kosis_comparison.md:housing_type`](../reports/tables/kosis_comparison.md)
- Could be wrong if: 적절한 개인 단위 housing reference 가 비교에 사용되면 격차가 줄어들 가능성.

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

[**C18**] (★★★) `housing_type` 의 직접 edge 는 단 2개 — district, occupation. 사람 속성 (age, sex, marital, family, education, bachelors_field) 과 모두 mediated 또는 no-edge.
- Evidence: [`data/processed/cmi/skeleton.json`](../data/processed/cmi/skeleton.json), [`data/processed/cmi/node_degrees.csv`](../data/processed/cmi/node_degrees.csv)

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
- Evidence: [`reports/figures/skeleton_compare.png`](../reports/figures/skeleton_compare.png)

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
- Evidence: [`data/processed/cmi/epsilon_counts.csv`](../data/processed/cmi/epsilon_counts.csv), [`data/processed/cmi/epsilon_boundary.csv`](../data/processed/cmi/epsilon_boundary.csv), [Phase 3 §2.5](../reports/PHASE3_REPORT.md#25-ε-threshold-sensitivity--위-결과는-임계-의존성이-얼마나-큰가)

[**C30**] (★★) Decoupling probe 는 단일 모델 (HGB) · 단일 seed 한정. 다른 모델 / seed 로 결과 다를 가능성.

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
C1  [_]  C7  [_]  C13 [_]  C19 [_]  C25 [_]
C2  [_]  C8  [_]  C14 [_]  C20 [_]  C26 [_]
C3  [_]  C9  [_]  C15 [_]  C21 [_]  C27 [_]
C4  [_]  C10 [_]  C16 [_]  C22 [_]  C28 [_]
C5  [_]  C11 [_]  C17 [_]  C23 [_]  C29 [_]
C6  [_]  C12 [_]  C18 [_]  C24 [_]  C30 [_]
```
