# 자주 묻는 질문 (FAQ)

## 일반

### Q. 이 리포는 NVIDIA를 비판하는 건가요?
아닙니다. NVIDIA의 데이터셋은 잘 만들어진 합성 데이터의 본보기 — 시도/시군구·인구학·교육 chain은 매우 충실합니다. 본 리포의 목적은 **사용자가 어디까지 이 데이터를 신뢰해야 할지** 판단할 수 있도록 *데이터 카드에 명시되지 않은 부분*을 정량화하는 것입니다.

### Q. NVIDIA가 데이터 카드에 검증 내용을 안 적었나요?
적혀 있긴 한데, **단변량 (marginal) 분포 수준** 의 정성 비교 위주입니다. 이변량 결합·조건부 독립성·예측 유틸리티 (TSTR / decoupling probe) 같은 지표는 공개되지 않았습니다. 본 리포가 이 빈자리를 채웁니다.

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
**예, 본래 용도(LLM 한국어 페르소나 학습)에는 괜찮습니다.** LLM 학습에는 텍스트의 다양성·자연스러움이 중요하고, 미세한 결합 분포 정확성은 덜 중요합니다. 본 리포의 우려는 **이 데이터를 통계 분석·정책 시뮬레이션 입력으로 쓸 때** 발생하는 것입니다.

---

## 방법론에 대한 질문

### Q. N=1,000,000 인데 χ² p-value 가 의미 없다고요?
네. 표본이 크면 *어떤 미세한 차이* 도 χ² 가 "통계적으로 유의" (p < 0.001) 로 판정합니다. 그래서 본 리포는 χ² 대신 **TVD, MI, CMI 같은 효과크기** 를 사용합니다. 효과크기가 작으면 (예: TVD < 0.01), 통계적으로 유의해도 실용적으로는 같다고 간주.

### Q. CMI 임계 ε = 0.005 nats 는 어떻게 정한 건가요?
변수 한 개의 엔트로피가 보통 0.5 ~ 2 nats 인 점을 고려해, "0.5%~ 1% 의 정보 공유" 를 효과 없는 수준으로 본 임의 임계입니다.

ε 를 변경하면 결과가 어떻게 바뀌는지는 [Phase 3 §2.5 sensitivity 분석](../reports/PHASE3_REPORT.md#25-ε-threshold-sensitivity--위-결과는-임계-의존성이-얼마나-큰가) 에서 정량화했습니다. 요약:
- ε 를 100배 변동 (0.0005 → 0.05) 시켜도 **direct edge 수는 32 → 13 사이** 에서만 움직임
- 23개 페어는 전 ε 범위에서 같은 분류를 유지 (ε-stable)
- 핵심 결론 (**housing decoupling**, demographic chain 강건성) 은 ε 변경에도 뒤집히지 않음
- 32개 boundary pair 는 임계에 민감 — 사용 시 주의

### Q. PC 알고리즘은 |Z| ≤ 2 까지만 했다는데, 더 가도 결과가 다를까요?
가능합니다. 본 리포가 'direct edge' 로 분류한 일부는 |Z| = 3 이상의 조합으로 매개될 수 있습니다. 다만:
1. |Z| 가 커질수록 조건부 표본이 작아지고, 노이즈가 커집니다 (1M 도 무한이 아님).
2. 본 리포의 핵심 결론 (housing decoupling, military as occupation function) 은 **이미 |Z| = 1 단계에서 명확히 보임** — 더 깊은 conditioning 으로 뒤집힐 가능성 낮음.

### Q. CMI 추정의 bias 는 어떻게 통제했나요? (occupation 2120 cats 같은 high-card 변수)
변수 카디널리티가 큰 페어는 plug-in MI 추정량이 upward bias 를 가집니다 (대략 (k-1)(m-1)/(2N) nats). occupation × district 의 경우 이 bias 만 0.27 nats 로 ε=0.005 의 53배입니다.

본 리포는 [Phase 3 §2.5](../reports/PHASE3_REPORT.md#25-permutation-null--bootstrap-ci--어느-edge-가-bias-가-아닌가) 에서 stratified permutation null (Y 를 Z 안에서 shuffle, 100회) 로 이 bias 를 정량화했습니다. 결과:
- **23개 direct edge 중 11개가 ratio_obs/null_p95 < 2 (bias-suspect)** — 모두 occupation/district 포함
- 가장 충격적: `occupation × district` marginal MI = 0.597 nats 중 97% 가 카디널리티 bias
- 견고한 결론은 12개 direct edge 만 (ratio > 2)
- **Housing decoupling 결론은 이 보정 후에도 견고** (housing × district ratio = 9.84)

### Q. Decoupling probe 결과의 info_added가 음수 (-0.008 nats) 인 게 무슨 의미죠?
음수는 **추가한 feature가 오히려 약간 과적합** 을 일으켜 holdout cross-entropy를 살짝 올렸다는 뜻. 사실상 0과 같으며, "person-attrs는 housing 예측에 정보를 더하지 못한다" 는 결론을 강하게 지지합니다. 단 단일 모델 (HGB) · 단일 시드 결과이므로 robustness 보강이 향후 작업 (P8: decoupling probe 다중 모델 / 시드).

### Q. "TSTR" 인가요, "decoupling probe" 인가요?
**Decoupling probe** 가 정확한 명칭입니다. 엄밀한 TSTR (Train on Synthetic, Test on Real) 은 *실제 한국 원자료* 에서 평가하는 것인데, 본 분석은 합성 데이터를 train/test split 한 **within-synthetic** probe 입니다. 표준 용어로 **predictive conditional-independence probe** 또는 **within-synthetic decoupling probe** 가 적절합니다.

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

### Q. GPT-5.5 Pro / Gemini 등으로 검증해보고 싶은데 어디서 시작?
1. [`review/REVIEW_PACKET.md`](../review/REVIEW_PACKET.md) 를 모델에 통째로 붙여넣기
2. [`review/REVIEW_PROMPTS.md`](../review/REVIEW_PROMPTS.md) 의 미리 작성된 프롬프트 중 하나 선택 (통합 리뷰 / falsification 모드 / 방법론 / 통계 / 도메인 / 재현성)
3. 결과를 issue (`external-review` 라벨) 로 공유

### Q. 패키지가 너무 큰가요? 모델 컨텍스트에 들어갈까요?
`REVIEW_PACKET.md` 는 그림 제외 약 ~17,000 토큰. Claude/GPT/Gemini 의 long-context 모드 (>100K) 에 충분히 들어갑니다. 그림은 별도로 첨부 또는 모델이 figure 텍스트 설명만 보고도 검증 가능하도록 작성.
