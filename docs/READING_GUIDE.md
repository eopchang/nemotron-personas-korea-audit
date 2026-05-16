# 읽기 가이드

이 리포에는 문서가 많습니다. 본인 상황에 맞는 길로 가세요.

---

## 🟢 "5분 안에 이 데이터의 신뢰도가 알고 싶다"

→ [README 의 "한 페이지 요약"](../README.md#-한-페이지-요약) 만 읽으세요.

---

## 🟡 "내 연구에 이 데이터를 쓸지 결정해야 한다"

1. [`docs/RESEARCHER_GUIDE.md`](RESEARCHER_GUIDE.md) — 사용 가능 / 불가 분석 체크리스트
2. [`reports/PHASE1_REPORT.md`](../reports/PHASE1_REPORT.md) §2 — 단변량 충실도 (5분)
3. [`reports/PHASE3_REPORT.md`](../reports/PHASE3_REPORT.md) §3 결정적 관찰들, §5 사용 권고 (10분)

---

## 🟠 "통계 방법론 자체가 궁금하다"

1. [`docs/GLOSSARY.md`](GLOSSARY.md) — CMI, NMI, PMI 등 용어 정리
2. [`docs/METHODOLOGY.md`](METHODOLOGY.md) — 본 리포가 쓴 방법론 종합
3. [`reports/PHASE3_REPORT.md`](../reports/PHASE3_REPORT.md) §1 방법, §6 한계
4. 코드 직접: [`scripts/_cmi.py`](../scripts/_cmi.py), [`scripts/_lib.py`](../scripts/_lib.py)

---

## 🔴 "이 분석을 의심한다 / 검증하고 싶다"

1. [`review/`](../review/) 디렉토리 전체 — 외부 모델 리뷰용 패키지
2. [`review/CLAIMS_LEDGER.md`](../review/CLAIMS_LEDGER.md) — 모든 주장에 번호 + 증거
3. [`review/REVIEW_PROMPTS.md`](../review/REVIEW_PROMPTS.md) — 다른 LLM에 그대로 붙여 쓸 수 있는 프롬프트
4. [`scripts/`](../scripts/) — 모든 분석 코드 (재현 가능)

---

## 🟣 "데이터셋 자체를 받아서 다른 분석을 하고 싶다"

1. [README §재현](../README.md#재현) 으로 환경 세팅
2. `python scripts/01_download.py` — HuggingFace 에서 받기 (~2GB)
3. [`scripts/_lib.py`](../scripts/_lib.py) 의 `load_df()` 호출하면 1M 행 polars DataFrame
4. 본 리포의 [`reports/PAIR_INDEX.md`](../reports/PAIR_INDEX.md) 에서 어느 변수 쌍에 강한 결합이 있는지 먼저 보세요.

---

## 🔵 "교육·강의 자료로 쓰고 싶다"

본 리포의 그림은 합성 데이터 평가 방법론 강의 / 정보이론 응용 사례로 적합합니다.

추천 자료:
- 단변량 충실도: [`reports/figures/compare_*.png`](../reports/figures)
- 이변량 결합: [`reports/figures/heatmap_theils_u.png`](../reports/figures/heatmap_theils_u.png) (방향성 비대칭)
- 매개 변수 검출: [`reports/figures/cmi_drop_heatmap.png`](../reports/figures/cmi_drop_heatmap.png)
- PGM 추론 결과: [`reports/figures/skeleton_compare.png`](../reports/figures/skeleton_compare.png)
- 결합 시각화 정수: [`reports/figures/threeway/`](../reports/figures/threeway)

라이선스 (CC BY 4.0) 에 따라 자유롭게 사용하시되 출처 표시 부탁드립니다.

---

## 📚 전체 문서 지도

```
README.md                                  — 시작점
├── docs/
│   ├── READING_GUIDE.md                   — (현재 보고 계신 문서)
│   ├── GLOSSARY.md                        — 용어집
│   ├── FAQ.md                             — 자주 묻는 질문
│   ├── RESEARCHER_GUIDE.md                — 사용 결정 가이드
│   └── METHODOLOGY.md                     — 방법론 종합
├── reports/
│   ├── PHASE1_REPORT.md                   — 단변량 충실도
│   ├── PHASE2_REPORT.md                   — 이변량 결합
│   ├── PHASE3_REPORT.md                   — PGM 구조 추론
│   ├── PAIR_INDEX.md                      — 55개 페어 색인
│   └── figures/                           — 모든 그림
├── review/
│   ├── REVIEW_PACKET.md                   — 외부 모델 리뷰용 단일 문서
│   ├── CLAIMS_LEDGER.md                   — 주장 → 증거 매핑
│   └── REVIEW_PROMPTS.md                  — 미리 작성된 리뷰 프롬프트
├── scripts/                               — 재현 코드
├── data/processed/                        — 작은 산출물 (commit)
└── data/raw/                              — 원본 (gitignore, 다운로드해야 함)
```
