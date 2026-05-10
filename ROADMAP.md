# Roadmap (앞으로의 작업)

본 리포는 단계적으로 검증을 강화해 나갑니다. 우선순위 순.

---

## P4 — CMI permutation null + bootstrap CI

고카디널리티 변수 (occupation 2,120, district 252) 의 plug-in MI bias 통제.
- Permutation null: Z strata 안에서 X(또는 Y) 를 shuffle 해 I(X;Y|Z) null distribution
- Block bootstrap: row bootstrap 으로 CMI 의 95% CI

이게 들어가면 임계 ε 를 임의로 정하는 대신 데이터 기반 threshold 가능.

---

## P5 — occupation KSCO 대분류 재코딩

2,120개 occupation 문자열을 KSCO (한국표준직업분류) 7차 대분류 10개로 재매핑한 뒤
주요 분석 (sex × occupation, education × occupation, age × occupation) 재실행.
KSCO 호환 결과는 통계청 공식 직업통계와 직접 비교 가능.

---

## P7 — KOSIS joint distribution 외부 비교

현재 KOSIS reference 는 marginal 만. Joint cross-tab 으로 확장:
- age × marital_status
- age × education_level
- sex × bachelors_field
- province × housing_type
- sex × occupation 대분류
- education × occupation 대분류

이게 들어가면 "내부적으로 그럴듯하다" → "실제 한국 joint distribution 과 비교했다" 로 격상.

---

## P8 — Decoupling probe 다중 모델 / 다중 시드

현재 단일 모델 (HGB) · 단일 시드 (42) 한계. 다음 robustness 추가:
- 5 seed 반복으로 표준오차
- LightGBM / RandomForest / multinomial logistic 추가
- Target permutation control
- District-stratified split
- HGB cardinality cap 변동 (250 / 500 / 1000)

특히 housing decoupling 의 info_added = -0.008 nats 가 sample 변동 대비 얼마나 견고한지 확정 필요.

---

## P9 — Phase 4: 페르소나 텍스트 bias audit

7개 자유서술 페르소나 텍스트 필드의 정량·정성 분석:
- 어휘 다양성 (vocabulary richness, distinct-n)
- 성별·연령별 직업·가족 역할 stereotype
- 지역 stereotype (수도권 vs 비수도권 묘사 차이)
- 고령층·저학력·무직 묘사 패턴
- 동일 demographic profile 의 텍스트 다양성 (paraphrase 다양성)

이 데이터셋의 본 용도가 LLM 학습용 페르소나임을 고려할 때 가장 실용적으로 중요한 검증.

---

## 참여하기

각 항목은 단독 작업 가능. 관심 있으시면 [issue](https://github.com/eopchang/nemotron-personas-korea-audit/issues) 로 의사 표명 후 진행하시면 됩니다.

외부 LLM 리뷰 (GPT-5.5 Pro / Gemini / 다른 Claude) 결과 공유도 환영. [`review/`](review/) 참고.
