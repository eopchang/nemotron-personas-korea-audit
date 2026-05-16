# 용어집 (Glossary)

본 리포에 자주 등장하는 용어를 가능한 한 친절하게 설명합니다.
순서는 알파벳/한글 가나다 순이 아니라 **개념 이해 순서** 입니다 — 위에서부터 읽으면 자연스럽게 다음 용어가 이어집니다.

---

## 데이터 자체에 대한 용어

### 합성 데이터 (Synthetic Data)
실제 사람의 정보가 **하나도 들어있지 않은**, 컴퓨터가 인공적으로 생성한 데이터.
"아무개 33세, 서울 강남구, 4년제 대학 졸업, 직업 사무원" 같은 행이 1백만 개 있어도,
이 안의 그 누구도 실존 인물이 아닙니다. 보통 **실제 통계 (KOSIS 등) 의 분포를 흉내 내도록** 만듭니다.

### 페르소나 (Persona)
한 사람을 묘사하는 가상의 인물. 본 데이터셋에서는 26개 변수 (성별, 나이, 직업, 자유서술 7종 등) 로 구성된 한 행이 한 페르소나.

### Probabilistic Graphical Model (PGM)
변수들 사이의 의존 관계를 **그래프(노드+엣지)** 로 표현하는 통계 모델.
- 노드 = 변수 (sex, age, occupation 등)
- 엣지 = "직접 영향을 주고받는다"
- 엣지가 없는 두 변수는 **다른 변수만 알면 서로 독립**.

NVIDIA의 데이터는 이런 PGM 으로 인구통계 변수를 표본 추출한 뒤, LLM 으로 자유서술 텍스트를 생성한 것입니다.

### KOSIS
국가통계포털 (kosis.kr). 통계청·행안부·각 부처의 공식 통계가 모여있는 사이트.
본 리포에서 reference 통계로 사용.

---

## 단변량 (Marginal) 분석 — Phase 1 핵심

### Marginal distribution (한계분포 / 단변량 분포)
변수 하나만 떼어 본 분포. "전체 인구 중 남자 49.6%, 여자 50.4%" 같은 것.
가장 기본적인 검증 — 합성 데이터의 marginal이 실제와 다르면 그 데이터는 일단 *시작부터* 잘못된 것.

### TVD — Total Variation Distance (총변동거리)
두 분포가 얼마나 다른지를 0~1 로 재는 지표.
```
TVD(P, Q) = ½ · Σ |P(i) − Q(i)|
```
- 0 = 완전히 같음
- 1 = 완전히 다름 (겹치는 카테고리 없음)
- 0.05 이내면 양호, 0.10 이상이면 검토 필요

직관: "각 카테고리에서 비율이 평균 몇 %p 차이 나는지" 의 절반 합.

### χ² (Chi-square) 검정
**작은 표본에서** 두 분포가 다른지를 통계적으로 판단하는 도구.
**대규모 데이터 (N=1M) 에서는 거의 모든 차이가 "통계적으로 유의" 로 나오므로 효과크기 (TVD 등) 만큼 정보가 많지 않음.** 본 리포는 χ² p-value를 보지 않는 이유.

---

## 이변량 (Bivariate) 분석 — Phase 2 핵심

### Cramér's V
두 카테고리 변수의 결합 강도. 0~1.
- ≥ 0.3 강함, ≥ 0.1 중간, ≥ 0.05 약함
- 카디널리티 (카테고리 개수) 영향을 받음 — 카테고리가 많으면 작아 보일 수 있음.

### Mutual Information (MI / 상호정보)
두 변수가 공유하는 정보량 (단위: nats 또는 bits).
```
I(X; Y) = ΣΣ p(x,y) · log [p(x,y) / (p(x)·p(y))]
```
- 0 = 두 변수가 독립 (서로 정보 없음)
- 양수 = 한 변수를 알면 다른 변수에 대한 불확실성이 줄어듦
- nats 단위는 자연로그 기반 (1 nat ≈ 1.44 bits)

### NMI — Normalized Mutual Information (정규화 상호정보)
MI 를 0~1 로 정규화한 것. 본 리포는 다음 식 사용:
```
NMI(X; Y) = 2 · I(X; Y) / [ H(X) + H(Y) ]
```
- 1.0 = 한 변수가 다른 변수를 완전 결정
- 0 = 독립

### Theil's U (Uncertainty Coefficient)
**비대칭** 결합 측도.
```
U(Y | X) = I(X; Y) / H(Y)
```
"X 를 알면 Y 의 불확실성이 몇 % 줄어드는가"
- U(Y|X) ≠ U(X|Y) — 방향성이 있음
- 예: U(시도 | 시군구) = 1.0 (시군구를 알면 시도가 결정됨)
       U(시군구 | 시도) ≈ 0.46 (시도를 알아도 시군구는 여러 후보)

### PMI — Pointwise Mutual Information (점별 상호정보)
하나의 *셀* (X=x, Y=y) 에서 독립과 얼마나 다른지.
```
PMI(x, y) = log [p(x, y) / (p(x)·p(y))]
```
- 양수: 그 조합이 독립일 때보다 더 자주 등장 (예: 4년제대 × 의사)
- 음수: 그 조합이 독립일 때보다 덜 등장 (예: 4년제대 × 건물청소원)
- 0: 정확히 독립 수준

PMI grid (heatmap) 는 **결합 분포에서 어디가 강한 신호인지** 한눈에 보여줌.

### Independence-deviation TVD
"결합분포가 독립이라면 어떻게 생겼을까" 와 실제 결합의 거리.
```
TVD( P(X,Y) ‖ P(X)·P(Y) )
```
- 0 = X와 Y는 독립
- 큰 값 = 강한 의존

---

## 다변량 (Multivariate) / 구조 추론 — Phase 3 핵심

### Conditional Independence (조건부 독립)
"Z 를 알고 나면, X 와 Y 는 더 이상 정보를 공유하지 않는다" → 표기: X ⊥ Y | Z.

예: 결혼상태와 학력은 둘 다 나이의 영향을 받음. 나이를 *모를 때* 는 둘이 상관 있어 보이지만,
나이를 *고정* 하고 보면 거의 독립. → 결혼 ⊥ 학력 | 나이.

### CMI — Conditional Mutual Information (조건부 상호정보)
조건부 독립을 정량화.
```
I(X; Y | Z) = ΣΣΣ p(x,y,z) · log [p(x,y,z)·p(z) / (p(x,z)·p(y,z))]
```
- I(X; Y | Z) ≈ 0 → "Z 만 알면 X·Y 는 서로 독립" → **Z 가 X-Y 결합의 매개**
- I(X; Y | Z) ≈ I(X; Y) → "Z 가 무관" → X-Y 사이에 직접 연결

본 리포의 핵심 도구.

### Mediator (매개 변수)
X 와 Y 가 통계적으로 결합된 진짜 이유가 다른 변수 Z 를 통한 것일 때, Z 를 매개라 부름.

예: "주차장 면적" 과 "교통사고 사망률" 은 도시별로 양의 상관. 매개는 "도시 인구". 도시 인구를 통제하면 두 변수의 상관은 사라짐.

본 리포에서 발견한 예: 결혼 ↔ 학력 의 결합 = 나이가 매개.

### Skeleton (스켈레톤)
PGM 의 **방향이 없는** 그래프 구조. 어느 변수 쌍이 직접 연결되어 있는가만 표시. (방향까지 알려면 추가 가정 필요)

### Direct edge (직접 엣지)
어떤 다른 변수를 조건으로 걸어도 CMI 가 살아있는 페어. → "이 두 변수는 PGM 에서 직접 연결됐다" 는 후보.

### Mediated edge (매개된 엣지) — 즉, **엣지가 없음**
다른 변수 하나를 조건으로 걸면 CMI ≈ 0 으로 떨어지는 페어. → 직접 연결이 아니라 다른 변수를 통한 의존.

### PC algorithm
PGM의 skeleton 을 데이터에서 추론하는 고전적 알고리즘. 페어마다 점점 큰 조건 변수 집합으로 독립성 검정.
본 리포는 |Z| ≤ 2 (조건 집합 크기 최대 2) 까지의 약식 버전 사용.

### ε threshold (CMI 임계)
CMI 가 이 값 미만이면 "효과 없음" 으로 본 임의 임계.
본 리포 기본값 ε = 0.005 nats (전체 엔트로피의 0.5~1% 정도). 이 임계가 결과를 얼마나 바꾸는지는 별도 sensitivity 분석에서 검증 (METHODOLOGY §5 참조).

---

## Bias 보정 도구 — Phase 3 §2.5 핵심

### Plug-in MI bias
표본에서 계산한 MI 추정량 (`MI_hat`) 이 진짜 MI 보다 위로 치우치는 현상.
2D contingency table 의 카디널리티가 크면 bias 도 큼 (Miller-Madow 보정값 ≈ (k−1)(m−1) / (2N)).
예: occupation × district (2120 × 252) 에서 bias ≈ 0.27 nats — 임계 ε=0.005 의 53배. → 단순 MI 값만으로는 "진짜 효과" 와 "추정 bias" 분간 불가.

### Permutation null (Stratified)
H0: X ⊥ Y | Z 하에서 X 와 Y 의 결합 분포가 어떨지 시뮬레이션하는 도구.
- **Unconditional (marginal)**: Y 를 전체에서 셔플 → I(X;Y) 의 null 분포
- **Stratified (conditional)**: Y 를 Z 의 각 stratum 안에서만 셔플 → I(X;Y|Z) 의 null 분포 (X·Y·Z 의 marginal 모두 보존, 결합만 깸)

관측값이 null 분포의 95th percentile 위에 있으면 "유의" (p < 0.05). 단 N 이 크면 거의 모든 게 유의해지므로 effect-size 비교가 더 정보적 — 아래 "ratio" 참조.

### Bootstrap CI (row bootstrap)
같은 N 으로 행을 with-replacement 재추출 → MI/CMI 분포 → 95% percentile = CI.
"추정치의 정밀도" (sampling variance) 를 잰다. permutation null 과 다른 정보:
- permutation null: "이 효과가 우연일 가능성"
- bootstrap CI: "추정치 자체가 얼마나 흔들리는가"

### Ratio = observed / null_p95
본 리포의 핵심 effect-size dominance 지표.
- ratio ≥ 10: robust — bias floor 의 10배 이상으로 견고
- ratio 2–10: significant — 통계적으로 분명하나 너무 강하진 않음
- ratio < 2: bias-suspect — 추정 bias 와 같은 자릿수, 진짜 의존성이라 단언 어려움

본 리포의 "23 direct edges 중 12개만 견고" 라는 분류는 이 ratio 임계 기반.

### Bias-corrected skeleton
원래 skeleton (PC-style 분류 결과) 에 위 permutation null ratio 를 입혀, robust/signif/suspect 3-tier 로 재분류한 의존 그래프. [`reports/figures/skeleton_bias_corrected.png`](../reports/figures/skeleton_bias_corrected.png) 가 본 리포의 메인 시각화.

---

## 분류기 기반 검증 — Phase 3 보강

### TSTR — Train on Synthetic, Test on Real
표준 정의: 합성 데이터로 모델을 학습한 뒤 *실제 데이터* 에서 평가하는 합성데이터 평가 방식.

**본 리포에서는 엄밀한 TSTR 을 수행하지 않는다.** 합성 데이터를 train/test split 한 *within-synthetic* 비교만 사용 — 정확한 명칭은 아래 "Decoupling probe".

### Decoupling probe (Predictive conditional-independence probe)
본 리포의 Phase 3 보강 분석. baseline feature set 과 baseline + extra feature set 으로 각각 분류기를 학습/평가한 뒤 cross-entropy 차이로 "extra 가 정보를 더하는가" 를 정량화.
- info_added ≈ 0 → extra 는 baseline 에 conditional independent
- info_added > 0 → extra 가 baseline 위에 정보 추가

본 리포의 housing decoupling 결정적 증거 산출법.

### Cross-Entropy (CE / 교차 엔트로피)
분류 모델이 정답을 얼마나 잘 맞추는지의 평균 정보량 손실 (단위: nats).
- 낮을수록 좋음
- 정답을 100% 확신하고 맞히면 CE = 0
- 무작위 추측이면 CE = H(target) (target의 엔트로피)

### Information added (정보 추가량)
```
info_added = CE(target | baseline_features) − CE(target | baseline + extras)
```
- 양수: 추가 feature가 도움됨
- 0 근처: 추가 feature가 불필요 (baseline 만으로 정보 포화)

본 리포의 **housing decoupling** 결정적 증거: info_added(person-attrs over district) = **−0.008 nats** (실질 0).

### Leakage check (데이터 누수 점검)
예측 모델 평가에서 train 데이터의 정보가 test 결과에 누설되는지 점검.
본 리포의 decoupling probe 는 6가지 잠재 누수 (encoder 전체 fit, cap_high_card 전체 빈도, target encoding, 단일 split, HGB 내부 split, 합성 row 중복성) 를 식별 후 **train-only encoder + 5-fold CV** 로 재실행 — 6개 case 모두 info_added 변화 < 0.005 nats (원본 효과의 1% 이하). 결론 변화 없음.

---

## 자주 쓰는 약어

| 약어 | 풀이 |
|---|---|
| MI | Mutual Information |
| CMI | Conditional MI |
| NMI | Normalized MI |
| TVD | Total Variation Distance |
| PMI | Pointwise MI |
| PGM | Probabilistic Graphical Model |
| PC algorithm | Peter-Clark algorithm (skeleton 추론) |
| ε (epsilon) | CMI 효과크기 임계 (본 리포 0.005 nats) |
| ratio | observed / null_p95 (effect-size dominance) |
| TSTR | Train on Synthetic, Test on Real |
| CV | Cross-Validation (5-fold 등) |
| CE | Cross-Entropy |
| HGB | HistGradientBoostingClassifier (sklearn) |
| KOSIS | 국가통계포털 |
| KSCO | 한국표준직업분류 |

---

## 더 읽을 거리 (외부)

- 합성 데이터 평가: SDV (synthetic-data-vault) 의 평가 가이드
- PGM / d-separation: Judea Pearl, *Causality* (2009) 1-2장
- 정보이론: Cover & Thomas, *Elements of Information Theory* 2장
- PC algorithm: Spirtes, Glymour, Scheines, *Causation, Prediction, and Search* (2000)
