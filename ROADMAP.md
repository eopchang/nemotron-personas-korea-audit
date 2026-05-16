# Roadmap (앞으로의 작업)

본 리포는 단계적으로 검증을 강화해 나갑니다. 우선순위 순.

---

## P5 — occupation KSCO 대분류 재코딩

2,120개 occupation 문자열을 KSCO (한국표준직업분류) 7차 대분류 10개로 재매핑한 뒤
주요 분석 (sex × occupation, education × occupation, age × occupation) 재실행.
KSCO 호환 결과는 통계청 공식 직업통계와 직접 비교 가능.

---

## P7 v2 — KOSIS joint distribution 완전 외부 비교 (남은 작업)

P7 v1 완료 (보도자료 인용 cell 기반 부분 검증, [Phase 3 §2.6](reports/PHASE3_REPORT.md#26-외부-검증--kosis--통계청-cross-tab-비교-p7-v1)).
v2 는 다음을 추가:

- **KOSIS Open API 키 등록 후 완전 cross-tab 다운로드** (DT_1IN1502 등)
- 17개 시도 × 6 housing_type 완전 cross-tab (현재 5 cell 만)
- 5세별 학력 표 (age × edu vintage 문제 해결)
- 추가: sex × bachelors_field (교육부/KEDI), sex × occupation 대분류 (P5 후), edu × occupation 대분류 (P5 후)

P7 v1 이 발견한 가설 (60대 여성 중졸이하 −44pp = PGM 고령층 학력 상향 편향?) 의 정밀 검증 필요.

---

## P8 — 합성-내 예측가능성 검사 다중 모델 / 다중 시드

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

외부 LLM 리뷰 (GPT / Gemini / 다른 Claude) 결과 공유도 환영. [`review/`](review/) 참고.
