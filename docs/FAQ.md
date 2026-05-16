# 자주 묻는 질문 (FAQ)

## 일반

### Q. 이 리포는 NVIDIA를 비판하는 건가요?
아닙니다. NVIDIA의 데이터셋은 잘 만들어진 합성 데이터의 본보기 — 시도/시군구·인구학·교육 chain은 매우 충실합니다. 본 리포의 목적은 **사용자가 어디까지 이 데이터를 신뢰해야 할지** 판단할 수 있도록 *데이터 카드에 명시되지 않은 부분*을 정량화하는 것입니다.

### Q. 단변량 12개 중 왜 5개만 KOSIS 와 비교했나요?
선정 기준은 **비교 가능성 + 우선순위** 의 조합입니다.

선정된 5개 (`sex`, `province`, `marital_status`, `education_level`, `housing_type`) 는 공식 KOSIS reference 와 카테고리·모집단이 명확히 매핑되는 변수.

나머지 7개의 탈락/미수행 이유 (※ `age_bin` 은 본 분석이 `age` 를 binning 해 만든 파생 변수로, 데이터셋 12개 변수에 포함되지 않음):

| 변수 | 탈락 / 미수행 이유 |
|---|---|
| `age` | **비교 가능하지만 본 phase 에서 미수행** — KOSIS 추계인구는 1세별/5세별 분포 공개. binning 정책 정해 1차 비교 우선순위에서 제외하고, 대신 [Phase 1 §1](../reports/PHASE1_REPORT.md#1-데이터셋-요약-실측) 에 기술통계 (평균 50.66, 중앙 51, std 17.6) 만 제시. 향후 보강 가능. |
| `country` | 단일값 (대한민국 100%) — 비교 무의미 |
| `district` | 252개 시군구 — 본 phase 에서 province (17) 비교로 갈음. 시군구 단위는 [ROADMAP P7 v2](../ROADMAP.md). |
| `family_type` | 39개 세분 카테고리 — 통계청 가구분류 (4-5개 대분류) 와 매핑 어려움 |
| `bachelors_field` | 전공 분포 — 25세+ vs 19세+ 모집단 차이, 공식 졸업자 성비 통계 부족 |
| `occupation` | 2,120개 직업명 — KSCO 7차 대분류 매핑 작업 필요 ([ROADMAP P5](../ROADMAP.md)) |
| `military_status` | KOSIS 추계인구는 군인을 별도 처리 — 직접 비교 어려움 |

→ KSCO 매핑 후 occupation 비교 + KOSIS joint cross-tab 비교 등은 [ROADMAP P5, P7](../ROADMAP.md).

### Q. 이변량 페어는 왜 55개인가요? (단변량은 12개인데)
`country` 는 단일값이라 결합 분석에서 의미 없음 → 결합 분석에는 11개 변수만 사용 → 11C2 = 11×10/2 = **55 페어**. (단변량 phase 에서는 country 포함 12개 모두 분포 산출은 했음, trivial 하지만.)

### Q. 이변량 55개 중 본문에서 깊이 다룬 10개는 어떻게 골랐나요?
5가지 선정 논리:
1. **NVIDIA 데이터카드 검증** — "직업 배정 시 성·전공이 독립" 주장 검증: `sex × bachelors_field`, `sex × occupation`
2. **Phase 1 격차 추적** — housing 격차의 원인 분석: `province × housing_type`
3. **결정론적 제약 검증** — "배우자있음 → 가구에 배우자 100%?": `marital_status × family_type`
4. **한국 도메인 핵심 결합** — 인구학·교육·노동: `age × {marital, education, occupation}`, `education × occupation`, `bachelors_field × occupation`
5. **Sanity check** — `sex × military_status` (현역 여성 비율)

나머지 45개도 [`reports/PAIR_INDEX.md`](../reports/PAIR_INDEX.md) 에서 NMI 순으로 확인 가능 + 자동 생성된 3-panel 그림 (`reports/figures/bivariate_all/`) 모두 제공.

### Q. PC-style 알고리즘이 정확히 뭐예요? 정통 PC 알고리즘과 다른가요?
**PC algorithm** (Peter-Clark, Spirtes & Glymour 1991) 은 PGM 의 skeleton 을 데이터에서 추론하는 고전적 알고리즘입니다.

**기본 절차**:
1. 모든 노드 쌍이 연결된 완전 그래프에서 시작
2. 각 페어 (X, Y) 마다 점점 큰 conditioning set Z 로 독립성 검정:
   - \|Z\|=0: 마지널 — `I(X;Y) < ε` 이면 edge 제거
   - \|Z\|=1: 다른 변수 하나로 조건걸어 `I(X;Y\|Z) < ε` 이면 제거
   - \|Z\|=2, =3, ... 점점 크게
3. 끝까지 살아남은 edge 가 "direct dependency"

**본 리포의 PC-style** 은 정통 PC 의 약식 변형:
- **\|Z\| ≤ 2 까지만** (정통 PC 는 이론적으로 \|Z\|=n−2 까지)
- 모든 subset 이 아니라 **best mediator + 1 추가** 의 휴리스틱
- 임계 ε = 0.005 nats 임의 선택 ([sensitivity 분석](../reports/PHASE3_REPORT.md#27-ε-threshold-sensitivity--위-결과는-임계-의존성이-얼마나-큰가) 완료)

이 한계 때문에 "skeleton 복원" 이 아니라 "skeleton 추정" 으로 표현.

### Q. Direct edge 와 Mediated edge 의 차이는?
세 가지 분류가 있습니다:

| 분류 | 정의 | 의미 | 예 |
|---|---|---|---|
| **direct** | `min_Z I(X;Y\|Z) ≥ ε` (어떤 Z 로 조건걸어도 의존 살아있음) | X-Y 직접 연결 | `marital × family_type` — 어떤 변수로 조건걸어도 NMI 살아있음 |
| **mediated** | `I(X;Y) ≥ ε` 이지만 `min_Z I(X;Y\|Z) < ε` (어떤 Z 로 조건걸면 의존 사라짐) | X-Y 결합은 Z 를 통한 간접 효과, 직접 연결 없음 | `marital × education_level` — 둘 다 age 의 함수, age 조건걸면 MI 0.105 → 0.004 |
| **no_edge_marginal** | `I(X;Y) < ε` (처음부터 의존 없음) | 거의 독립 | `sex × housing_type` (NMI ≈ 0) |

자세한 정의는 [`docs/GLOSSARY.md`](GLOSSARY.md#mediated-edge-매개된-엣지--즉-엣지가-없음).

### Q. NVIDIA가 데이터 카드에 검증 내용을 안 적었나요?
적혀 있긴 한데, **단변량 (marginal) 분포 수준** 의 정성 비교 위주입니다. 이변량 결합·조건부 독립성·예측 유틸리티 (TSTR / 합성-내 예측가능성 검사) 같은 지표는 공개되지 않았습니다. 본 리포가 이 빈자리를 채웁니다.

### Q. 1백만 행에 700만 페르소나라니, 이상한 표현 아닌가요?
NVIDIA의 표기 방식입니다. 한 행에 7개의 자유서술 페르소나 텍스트 (직업·스포츠·예술·여행·식문화·가족·요약) 가 있어, 1M × 7 = "약 700만 페르소나" 로 마케팅. 행 수는 1,000,000.

---

## 발견 사항에 대한 질문

### Q. "Housing decoupling" 이 뭔가요? 왜 중요한가요?
- **Decoupling = 분리됨**. 합성 데이터 안에서 housing_type 변수가 사람 속성(나이·결혼·가족·직업 등) 과 통계적으로 분리되어 있음.
- 의미: 1인 가구도, 4인 가족도, 청년도, 노년도 모두 같은 주거 분포 (아파트 ~62%) 를 보임.
- 현실 (정성적): 한국에서 1인 가구는 오피스텔/원룸 비중이 더 높고 청년은 임대 비중이 높다는 일반적 인식과 다름. 단 정확한 정량 비교를 위해서는 KOSIS 의 *개인 단위* (또는 가구주 단위) 주거 cross-tab 과 직접 대조해야 함.
- 영향: 개인 속성별 주거 분석 (예: 청년 주거, 1인 가구 주거 형태 비교, 학력별 주거) 에 본 데이터 부적합. *지역 단위* 주택 유형 시뮬레이션은 별개로 사용 가능.

### Q. "Military_status는 occupation 함수" 가 무슨 뜻?
- 데이터 안에서 "현역" 라벨이 붙은 행은 거의 100% 직업이 "육군 부사관", "공군 장교", "육군 병사" 등 군 직업 12개 중 하나.
- 즉 PGM에서 military_status는 독립 노드라기보다 occupation 라벨에서 파생된 부수 변수에 가까움.
- 영향: military_status 와 occupation 을 동시에 모델 입력으로 쓰면 정보 중복.

### Q. 그러면 현역 평균 연령이 40.9세인 게 이상하지 않나요?
이상하지 않습니다. `military_status = 현역` 은 "의무복무 *이행 중*" 이 아니라 **"현역 군 인력 신분 (직업군인 + 의무복무 통합)"** 의미로 사용됐습니다 (미국식 'active duty' 에 가까움). 계급별로 분해하면:

| 계급 | 평균 연령 | 최대 | 여성 |
|---|---:|---:|---:|
| 병사 (의무복무) | 25.4 | 30 | 0% |
| 부사관 (직업) | 40.6 | 55 | 11% |
| 장교 (직업) | 46.7 | 63 | 11% |

한국군 부사관 정년 53-58세, 장교 정년 56-63세, 여성 의무복무 부재 — 모두 정확히 반영됩니다. **의무복무 흐름**(입영·전역 동학) 분석에는 부적합하지만 **현역 인력 cross-section 구성** 분석은 가능합니다.

### Q. 그러면 이 데이터를 LLM 학습에 써도 괜찮은가요?
**예, NVIDIA 가 명시한 본래 용도 (LLM 학습 / 합성 데이터 다양성 확대 / 모델 편향 완화 / 소버린 AI 개발) 에는 괜찮습니다.** LLM 학습에는 텍스트의 다양성·자연스러움이 중요하고, 미세한 결합 분포 정확성은 덜 중요합니다. 본 리포의 우려는 **이 데이터를 통계 분석·정책 시뮬레이션 입력으로 쓸 때** 발생하는 것입니다.

---

## 방법론에 대한 질문

### Q. N=1,000,000 인데 χ² p-value 가 의미 없다고요?
네. 표본이 크면 *어떤 미세한 차이* 도 χ² 가 "통계적으로 유의" (p < 0.001) 로 판정합니다. 그래서 본 리포는 χ² 대신 **TVD, MI, CMI 같은 효과크기** 를 사용합니다. 효과크기가 작으면 (예: TVD < 0.01), 통계적으로 유의해도 실용적으로는 같다고 간주.

### Q. CMI 임계 ε = 0.005 nats 는 어떻게 정한 건가요?
변수 한 개의 엔트로피가 보통 0.5 ~ 2 nats 인 점을 고려해, "0.5%~ 1% 의 정보 공유" 를 효과 없는 수준으로 본 임의 임계입니다.

ε 를 변경하면 결과가 어떻게 바뀌는지는 [Phase 3 §2.7 sensitivity 분석](../reports/PHASE3_REPORT.md#27-ε-threshold-sensitivity--위-결과는-임계-의존성이-얼마나-큰가) 에서 정량화했습니다. 요약:
- ε 를 100배 변동 (0.0005 → 0.05) 시켜도 **direct edge 수는 32 → 13 사이** 에서만 움직임
- 23개 페어는 전 ε 범위에서 같은 분류를 유지 (ε-stable)
- 핵심 결론 (**housing decoupling**, demographic chain 강건성) 은 ε 변경에도 뒤집히지 않음
- 32개 boundary pair 는 임계에 민감 — 사용 시 주의

### Q. PC 알고리즘은 |Z| ≤ 2 까지만 했다는데, 더 가도 결과가 다를까요?
가능합니다. 본 리포가 'direct edge' 로 분류한 일부는 |Z| = 3 이상의 조합으로 매개될 수 있습니다. 다만:
1. |Z| 가 커질수록 조건부 표본이 작아지고, 노이즈가 커집니다 (1M 도 무한이 아님).
2. 본 리포의 핵심 결론 (housing decoupling, military as occupation function) 은 **이미 |Z| = 1 단계에서 명확히 보임** — 더 깊은 conditioning 으로 뒤집힐 가능성 낮음.

### Q. KOSIS 와 외부 비교는 했나요? (joint distribution 수준)
부분 완료 ([Phase 3 §2.6](../reports/PHASE3_REPORT.md#26-외부-검증--kosis--통계청-cross-tab-비교-p7-v1)). KOSIS 직접 API 접근이 SSO redirect / JS 동적 로딩으로 막혀, 공식 보도자료·정책브리핑·한국의 사회동향 인용 cell 만 비교한 P7 v1:
- **age × marital × sex** (8/8 cell ±4pp 이내) — ★★★ 강한 외부 일치
- **province × housing** (5/6 cell ±3pp, 전국 합계만 ±9pp) — 시도 패턴 일치, aggregate offset 은 가구↔개인 단위 차이
- **age × sex × education** ⚠️ — reference vintage (2014) 문제로 60대 여성 중졸이하 −44pp 등 큰 격차. PGM 고령층 학력 상향 편향 *가능성* 이지만 코호트 갱신과 분리 불가 → P7 v2 에서 2020 census 5세별 학력으로 정밀 재검증 필요.

### Q. housing 의 격차는 얼마나 큰가요? NVIDIA 의 marginal-level 실수인가요?
**TVD ≈ 0.08 의 약한 격차** ([Phase 1 §3-4](../reports/PHASE1_REPORT.md#3-4-housing_type----약한-격차)).

Nemotron 은 개인 단위 (1M 행 = 1M 명) 이므로 per-person 거처 분포 reference 와 비교해야 합니다. 공식 per-person 통계가 별도 발표되지 않아 본 분석이 자체 추정 (통계청 일반가구 + 1인가구 비중·거처분포 + 평균 가구원수 가중).

셀별 격차:
- 아파트 +3.5pp, 단독주택 −8pp, 연립·다세대 +3pp, 주택이외 +2pp
- 단독주택 -8pp 가 가장 큰 차이지만 reference 자체 추정 오차 (±2pp) 고려 시 단언 어려움
- "NVIDIA 의 실수" 라기보다는 잔존하는 작은 차이로 해석. Phase 3 의 housing decoupling 결론 (sex/age/marital 무관) 은 internal structure 분석이라 이 격차와 무관.

### Q. CMI 추정의 bias 는 어떻게 통제했나요? (occupation 2120 cats 같은 high-card 변수)
변수 카디널리티가 큰 페어는 plug-in MI 추정량이 upward bias 를 가집니다 (대략 (k-1)(m-1)/(2N) nats). occupation × district 의 경우 이 bias 만 0.27 nats 로 ε=0.005 의 53배입니다.

본 리포는 [Phase 3 §2.5](../reports/PHASE3_REPORT.md#25-permutation-null--bootstrap-ci--어느-edge-가-bias-가-아닌가) 에서 stratified permutation null (Y 를 Z 안에서 shuffle, 100회) 로 이 bias 를 정량화했습니다. 결과:
- **23개 direct edge 중 11개가 ratio_obs/null_p95 < 2 (bias-suspect)** — 모두 occupation/district 포함
- 가장 충격적: `occupation × district` marginal MI = 0.597 nats 중 97% 가 카디널리티 bias
- 견고한 결론은 12개 direct edge 만 (ratio > 2)
- **Housing decoupling 결론은 이 보정 후에도 견고** (housing × district ratio = 9.84)

### Q. 예측가능성 검사 결과의 info_added가 음수 (-0.008 nats) 인 게 무슨 의미죠?
음수는 **추가한 feature가 오히려 약간 과적합** 을 일으켜 holdout cross-entropy를 살짝 올렸다는 뜻. 사실상 0과 같으며, "person-attrs는 housing 예측에 정보를 더하지 못한다" 는 결론을 강하게 지지합니다. 단일 모델 (HGB) 한계는 향후 작업 (P8). **5-fold CV 보강** 완료: 5-fold SE < 0.02 nats, leakage-corrected 결과 -0.0082 로 거의 동일.

### Q. 예측가능성 검사 에 data leakage 이슈는 없었나요?
정밀 점검 완료 ([Phase 3 §1.4](../reports/PHASE3_REPORT.md#14-leakage-check--위-probe-결과는-데이터-누수에-영향받았나)). 잠재 leakage 6가지 (전체 데이터로 OrdinalEncoder fit, cap_high_card 전체 빈도 기반 등) 를 식별 후 train-only encoder + 5-fold CV 로 재실행. **6개 모든 case 에서 info_added 변화 < 0.005 nats** (원본 효과의 1% 이하). 결론 (Q1 housing decoupled, controls 모두 작동) 그대로 유지. 우려는 합리적이었으나 실제 영향은 무의미.

---

## 데이터 사용

### Q. 데이터셋을 받으려면?
```bash
python scripts/01_download.py
```
HuggingFace 에서 자동으로 받습니다 (~2GB, 9개 parquet shard). 별도 인증 불필요.

### Q. 본 리포의 산출물을 인용하려면?
[`CITATION.cff`](../CITATION.cff) 의 메타데이터를 사용하세요. GitHub 가 자동으로 BibTeX/APA 변환해줍니다.

### Q. 결과를 비판/반박하고 싶다면?
환영합니다. [`CONTRIBUTING.md`](../CONTRIBUTING.md) 참고. 가장 가치 있는 기여는 본 리포의 결론을 정정하는 것입니다.

---

## 다른 LLM 으로 검증

### Q. GPT / Gemini / Claude 등 최신 모델로 검증해보고 싶은데 어디서 시작?
1. [`review/REVIEW_PACKET.md`](../review/REVIEW_PACKET.md) 를 모델에 통째로 붙여넣기
2. [`review/REVIEW_PROMPTS.md`](../review/REVIEW_PROMPTS.md) 의 미리 작성된 프롬프트 중 하나 선택 (통합 리뷰 / falsification 모드 / 방법론 / 통계 / 도메인 / 재현성)
3. 결과를 issue (`external-review` 라벨) 로 공유

### Q. 패키지가 너무 큰가요? 모델 컨텍스트에 들어갈까요?
`REVIEW_PACKET.md` 는 그림 제외 약 ~35,000 토큰. GPT / Claude / Gemini 등의 최신 long-context 모델에 충분히 들어갑니다. 그림은 별도로 첨부 또는 모델이 figure 텍스트 설명만 보고도 검증 가능하도록 작성.
