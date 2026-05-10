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

ε = 0.005 nats. Sensitivity 분석은 미실시 (TODO).

### 4.4 한계
- |Z| ≤ 2 까지만. |Z| ≥ 3 mediation 가능성은 확인 안 함.
- 방향성 미해결 (DAG 아닌 skeleton).

---

## 5. Predictive decoupling probe — Phase 3 보강

> 용어 주의: 본 within-synthetic probe 는 엄밀한 TSTR (Train on Synthetic, *Test on Real*) 과 다르다. 합성 데이터만으로 train/test split 한 **predictive conditional-independence probe** / **decoupling probe** 가 정확한 명칭.

### 5.1 목표
"Feature set F 가 baseline B 위에 정보를 더하는가" 를 분류기 cross-entropy로 측정.

### 5.2 모델
- `sklearn.HistGradientBoostingClassifier`
- 200 iter, max_depth=8, lr=0.05
- 모든 feature를 categorical로 처리 (OrdinalEncoder + categorical_features mask)

### 5.3 Cardinality 처리
HGB의 categorical 한계 (255 unique). 250 초과는 top-249 + "기타" 로 캡.

### 5.4 데이터 분할
- 300,000 행 subsample (시드 42)
- 80/20 train/test, random split (stratify 미사용)

### 5.5 지표
- Cross-Entropy (CE), nats, log_loss with all classes
- Accuracy
- info_added = CE_baseline − CE_full

### 5.6 해석
- info_added ≈ 0: 추가 feature가 baseline 위에 정보를 더하지 못함 → conditional independence
- info_added > 0: 정보 추가 (real signal)
- info_added < 0: 추가 feature가 약간의 과적합. 사실상 0.

---

## 6. Subsample stability — Phase 3 보강

### 6.1 절차
- N_SUB = 200,000, N_SEEDS = 5
- 각 시드에서 |Z|=1 까지의 skeleton classification 재계산
- 분류 일치율 = 5/5 시드에서 동일하면 stable

### 6.2 결과
55 페어 중 52개 stable (94.5%). 3개 unstable은 |Z|=1 vs |Z|=2 방법론 mismatch이지 데이터 노이즈가 아님.

---

## 7. 모든 임의 선택 / 임계 한 곳에 모음

| 매개변수 | 값 | 위치 |
|---|---|---|
| age binning | [19-24, 25-34, ..., 85+] | `_lib.py:AGE_BREAKS` |
| TVD "양호" 임계 | < 0.05 (subjective) | PHASE1_REPORT §2 |
| CMI 효과크기 임계 ε | 0.005 nats | `08_skeleton_recovery.py:EPSILON` |
| PC conditioning depth | \|Z\| ≤ 2 | `08_skeleton_recovery.py` |
| Decoupling probe subsample size | 300,000 | `11_decoupling_probe.py:N_SUB` |
| Probe HGB iter | 200 | `11_decoupling_probe.py:fit_eval` |
| HGB cardinality cap | 250 | `11_decoupling_probe.py:CARD_CAP` |
| Stability subsample | 200,000 × 5 seeds | `12_subsample_stability.py` |
| Visualization topK occupation | 20 | `05b_bivariate_detail_all.py:TOPK` |
| Visualization topK district | 25 | `05b_bivariate_detail_all.py:TOPK` |

→ 이 임계들 중 본 리포 결론에 가장 영향이 클 만한 것은 **CMI 임계 ε 와 PC depth |Z|**.
   sensitivity 분석은 future work.

---

## 8. 재현성 체크리스트

- [x] 모든 random seed 명시 (42 / 0..4)
- [x] 모든 임계 코드에 명시
- [x] requirements.txt 버전 fix
- [x] 한 명령으로 phase별 재실행 가능
- [x] 산출물 (CSV/JSON) git에 commit (작은 것)
- [ ] CI (GitHub Actions) 로 smoke test (TODO)
- [ ] Docker 이미지 (TODO)
