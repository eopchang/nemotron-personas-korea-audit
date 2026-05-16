# 외부 모델 리뷰 프롬프트

GPT-5.5 Pro / Claude Opus / Gemini Pro 등에 그대로 붙여넣을 수 있는 프롬프트 모음.

**사용법**: 모델에 먼저 [`REVIEW_PACKET.md`](REVIEW_PACKET.md) 를 첨부 또는 paste 하고,
그 다음에 아래 프롬프트 중 하나를 붙여 넣으세요.

---

## 🎯 프롬프트 0a — Falsification 모드 (가장 강한 비판 유도)

```text
당신은 합성 데이터 평가에 능통한 시니어 통계학자입니다.
첨부된 REVIEW_PACKET 의 결론들을 **반박** 하려고 시도해주세요. 친절한 검토가 아니라
적극적 비판입니다.

다음 형식으로 응답:

【1】본 리포트의 핵심 결론 7개 (시도/시군구 분포, 인구학 chain, 성별×전공, housing decoupling, military as occupation function, occupation '무직' 카테고리, high-card bias 등 — README "7개 결정적 발견" 참조)
   각각에 대해 "이 결론을 무너뜨리려면 어떤 분석 결과가 나와야 하는가" 를 적어주세요.
   각 결론마다 falsification test 1-2개 제안.

【2】본 리포트의 문장 중 evidence level 대비 과장된 표현을 찾아 직접 인용하고
   더 안전한 수정안을 제시해주세요. 최소 5개.

【3】CLAIMS_LEDGER 의 36개 주장 중 신뢰도 등급이 *과대* 매겨졌다고 보는 것을
   3개 이상 골라 다운그레이드 사유와 함께 적어주세요.

【4】본 리포트의 결론 중 외부에서 신뢰하기 어려운 가장 약한 부분 1개를
   골라, 추가로 어떤 검증이 들어가야 신뢰할 만해지는지 구체적으로 적어주세요.

당신은 NVIDIA 측 변호사처럼 행동해도 좋습니다 — 즉 본 검토가 NVIDIA 의 데이터셋을
부당하게 깎아내린 부분이 있다면 그것도 짚어주세요.
```

---

## 🎯 프롬프트 0 — 통합 리뷰 (가장 많이 사용)

```text
당신은 통계학·정보이론·합성 데이터 평가에 능통한 시니어 연구자입니다.
앞서 첨부된 REVIEW_PACKET 에는 NVIDIA가 공개한 한국인 합성 페르소나 데이터셋
(Nemotron-Personas-Korea, 1M 행) 에 대한 독립 검토 결과가 들어있습니다.

다음 4개 측면에서 이 검토를 객관적으로 평가하고, 마지막에 종합 판단을 내려주세요.

【1. 방법론 적합성】
- Conditional Mutual Information (CMI) 계산이 표준 정의와 일치하는가
- PC-style skeleton recovery 의 |Z| ≤ 2 한계가 결론을 얼마나 약화시키는가
- Decoupling probe 의 설계 (HGB, 300K subsample, info_added) 가 의도한 측정을 정확히 하는가
- 빠뜨린 표준 검증 도구가 있는가 (예: pMSE, discriminator AUC, propensity score 차이)

【2. 통계적 정당성】
- 효과크기 임계 (TVD < 0.05, ε = 0.005 nats) 가 적절한가
- N=1M 에서 χ² 를 무시하고 효과크기만 본 결정이 합리적인가
- Decoupling probe 결과의 info_added = -0.008 nats 가 정말 "0"으로 해석 가능한가 (단일 모델 한계, 표본 변동 고려 후)
- 안정성 체크 (5 seed × 200K) 가 충분한가

【3. 도메인 해석 (한국 인구통계)】
- KOSIS / 통계청 reference 통계가 정확하게 인용됐는가
- 한국 인구학 패턴 해석 (사별률, 코호트 학력, 군 복무 연령) 이 한국 현실과 부합하는가
- "housing decoupling" 결론이 한국 주거 현실과 비교해 정당한가
- "military as occupation function" 해석이 과한가, 적절한가

【4. 재현성·투명성】
- CLAIMS_LEDGER 의 36개 주장 중 증거가 명확한 것 / 모호한 것
- 코드와 산출물의 매핑이 명확한가
- 임의 선택 (임계, 시드, 샘플 크기) 이 충분히 명시됐는가

【종합 판단】
다음 형식으로 마무리:
- 본 검토의 핵심 결론 7개를 최대 신뢰도 / 보통 / 낮은 신뢰도로 분류
- 가장 큰 약점 3개
- 추가로 수행하면 좋을 검증 3개
- "이 검토를 인용해도 될 만한 신뢰도인가" 1줄 평
```

---

## 🔬 프롬프트 1 — 방법론 집중 리뷰

```text
당신은 PGM (Probabilistic Graphical Model) · 정보이론 · 인과추론에 능통한 시니어 통계학자입니다.
첨부된 REVIEW_PACKET 의 Phase 3 (PGM 구조 추론) 부분을 집중 검증해주세요.

확인할 점:

1. CMI 정의·구현
   - I(X;Y|Z) 의 nats 단위 계산이 표준과 일치하는가
   - 3D contingency 기반 추정의 한계 (sparse cells, plug-in bias) 가 본 결과에 영향을 줄 정도인가
   - 사용된 추정량 (plug-in MLE) 외에 더 나은 대안 (MIXED, kNN-based) 이 있는가

2. PC-style skeleton recovery
   - 본 구현이 정확한 PC 알고리즘과 어떻게 다른가 (|Z| ≤ 2, single-Z first 등)
   - 'best mediator + 1 more' 휴리스틱이 정통 PC 의 power-set conditioning 보다 얼마나 더 보수적/공격적인가
   - 결과 skeleton 에서 빠진 가능한 edge / 잘못 포함된 edge 의 후보를 짚어보라

3. Decoupling probe (within-synthetic predictive conditional-independence)
   - HistGradientBoostingClassifier 가 categorical 변수 의존을 잘 잡는가, 또는 약간의 dependency 를 놓칠 수 있는가
   - log_loss 차이를 nats 로 해석하는 절차가 올바른가
   - 단일 random seed (42) 에 의존한 점, stratify 미사용 등의 효과
   - "info_added < 0" 의 통계적 의미

4. 다음 중 어느 것이 본 분석의 결론을 가장 크게 바꿀 수 있는가:
   - |Z| 를 3 또는 power set 으로 확장
   - 부드러운 추정량 (regularized) 사용
   - 블록 부트스트랩으로 CMI 의 신뢰구간 산출
   - 다른 구조 학습 알고리즘 (NOTEARS, GES, GraNDAG)

응답 길이: 1500-2500 단어
형식: 위 4개 섹션 각각에 대해 (a) 평가 (b) 구체적 우려 (c) 권고
```

---

## 📊 프롬프트 2 — 통계적 정당성 집중

```text
당신은 효과크기 (effect size) 와 대규모 표본 통계 해석에 능통한 데이터 과학자입니다.
첨부된 REVIEW_PACKET 의 모든 임계와 임의 선택을 평가해주세요.

평가 대상 (METHODOLOGY §7 표 참조):
1. age binning [19-24, 25-34, ..., 85+]
2. TVD "양호" 임계 < 0.05
3. CMI 효과크기 임계 ε = 0.005 nats
4. PC conditioning depth |Z| ≤ 2
5. Decoupling probe subsample size 300,000
6. HGB 200 iter / depth 8 / lr 0.05
7. HGB cardinality cap 250
8. Stability 200,000 × 5 seeds

각각에 대해:
- 이 선택이 본 리포의 결론을 얼마나 강하게 만들거나 약하게 만드는가
- 더 보수적인 / 더 공격적인 대안 임계는?
- sensitivity 분석을 한다면 어떤 결과가 나올 것 같은가

특히 답해주세요:
A. CMI 임계 ε 를 0.001 또는 0.01 로 바꾸면 23개 direct edge 중 몇 개가 어떤 방향으로 바뀔까
B. Decoupling probe 의 info_added = -0.008 nats 가 sample 변동 대비 얼마나 신뢰할 수 있는가
   - 5 seed × HGB 로 표준오차 산출 시 대략 어느 정도일 것 같은가
C. N=1M 에서 χ² p-value 무시 결정의 정당성

마지막에 "본 리포가 가장 보강해야 할 통계적 robustness check 3개" 를 우선순위 순으로.
```

---

## 🇰🇷 프롬프트 3 — 한국 도메인 검증

```text
당신은 한국 인구통계·노동·주거 연구에 정통한 도메인 전문가입니다 (또는 한국 사회과학 박사 수준의 지식이 있습니다).
첨부된 REVIEW_PACKET 의 한국 현실 해석 부분을 검증해주세요.

확인할 사항:

1. KOSIS / 통계청 reference 수치 정확성
   - data/reference/kosis_reference.json (REVIEW_PACKET 에 수록) 의 6개 reference 분포가
     실제 KOSIS / 통계청 공표 수치와 일치하는가
   - 모집단 정의 (15+, 19+, 25+, 가구, 개인) 차이로 인한 caveat 처리가 적절한가
   - 더 적합한 reference (다른 연도, 다른 통계) 가 있는가

2. 한국 인구학 패턴 해석 정당성
   - 19-24 미혼 95.4%, 25-34 미혼 65.3% 가 한국의 만혼·비혼 추세와 부합하는가
   - 75-84 사별 42.6%, 85+ 사별 70.7% 가 평균 수명 차이와 부합하는가
   - 25-34 4년제 학력 51.6%, 85+ 무학 37.4% 가 한국 코호트 교육 변화와 부합하는가
   - 65세 이상 무직 패턴이 한국 정년·연금 제도와 부합하는가

3. 핵심 우려 사항의 도메인 정당성
   - 현역 인력 분해 (병사 25세 / 부사관 41세 / 장교 47세, 여성 11%) 가 한국군 실제 인력 구성과 부합하는가 — `data/processed/military_breakdown.json` 참조
   - "혼자 거주" 비율 약 14% (개인 단위) vs 통계청 2023 1인가구 35% (가구 단위) — 본 리포가 단위 차이로 인한 직접 비교 불가능을 명확히 짚었는가 (RESEARCHER_GUIDE 결혼·가족 분석 § 참조)
   - "공학 86% 남성, 보건 28% 남성" 이 한국 4년제 졸업자 성비 통계와 정확히 부합하는가
   - "housing decoupling" 이 한국 주거 시장 (1인 가구 오피스텔, 청년 임대) 의 현실과 비교해 정당한 우려인가

4. 본 리포가 도메인 관점에서 놓친 분석
   - 어떤 한국적 패턴이 검증돼야 했는데 안 됐는가
   - 농어촌 vs 도시, 수도권 vs 비수도권 같은 대분류 비교가 더 풍부할 수 있었는가
   - 출신지·이주 패턴, 외국인·다문화 가구 등 본 데이터가 다루지 않는 측면

마지막에:
- 본 리포의 한국 도메인 해석 중 가장 신뢰할 만한 것 3개
- 가장 의심스러운 것 3개
- 한국 사회과학자가 본 데이터를 사용하기 전 추가로 확인해야 할 사항
```

---

## 🔧 프롬프트 4 — 재현성·코드 검증

```text
당신은 데이터 과학 재현성 (reproducibility) 평가 전문가입니다.
첨부된 REVIEW_PACKET 의 코드 / 데이터 / 산출물 매핑을 점검해주세요.

평가 대상:

1. CLAIMS_LEDGER 의 36개 주장 → 증거 파일 매핑
   - 각 주장이 어떤 CSV/JSON/figure 에서 직접 검증 가능한가
   - 매핑이 명확하지 않은 주장은 어느 것인가

2. 임의 선택의 명시 정도
   - 본 리포가 사용한 모든 시드 (random seed) 가 명시됐는가
   - 임계, 표본 크기, 전처리 결정이 코드에 명시 + METHODOLOGY 에 정리됐는가

3. 환경 / 의존성
   - requirements.txt 가 충분한가 (버전 핀 포함)
   - 비결정성 요소 (예: HGB 의 multi-thread, scikit-learn 버전 차이) 가 있는가

4. 코드 → 산출물 → 리포트의 일관성
   - 각 phase 의 결과 수치가 코드 출력과 정확히 일치하는가 (REVIEW_PACKET 의 key_results.json 활용)
   - 리포트의 표/그림이 산출물 파일에서 직접 만들어진 것인지 확인 가능한가

5. 제3자 재현 가능성
   - 신규 사용자가 README 만 보고 모든 결과를 재생산할 수 있는가
   - 빠진 documentation 이나 환경 설정 단계가 있는가
   - 데이터 다운로드 (HuggingFace) 외 외부 의존성이 있는가

이슈를 발견하면 다음 형식:
- 이슈: 무엇이 빠지거나 잘못됐는가
- 영향: 본 리포의 어떤 결론이 영향받는가
- 권고: 어떻게 고치면 좋은가

마지막에 "재현성 점수" 1-10 + 이유.
```

---

## 💡 사용 팁

- **RAG 가 아닌 long-context 모델** 사용 권장 (전체 PACKET 을 한 번에 읽어야 일관성 있는 평가)
- 모델이 KOSIS 수치를 의심하면, 실제 KOSIS 사이트를 검증할 수 있는 Web search / browsing 기능 활성화 도움
- 결과를 [`.github/ISSUE_TEMPLATE/external_review.md`](../.github/ISSUE_TEMPLATE/external_review.md) 양식으로 issue로 공유 부탁드립니다
