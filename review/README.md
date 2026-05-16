# 외부 리뷰 키트

본 리포의 분석을 GPT-5.5 Pro, Gemini, 다른 Claude, 또는 사람 동료가
**독립적으로 점검** 할 수 있도록 준비된 패키지.

---

## 🎯 왜 이 키트인가

본 리포는 NVIDIA의 데이터셋에 대해 비교적 강한 주장을 합니다 (예: "housing은
사람 속성과 decoupled"). 이런 주장의 신뢰도는 *외부 검증*을 받을수록 올라갑니다.
이 디렉토리는 **외부 검증을 가능한 한 마찰 없이** 만들기 위한 것입니다.

---

## 📦 무엇이 들어있나

| 파일 | 용도 |
|---|---|
| [`REVIEW_PACKET.md`](REVIEW_PACKET.md) | **단일 파일에 모든 것** — 리뷰어 모델에 그대로 붙여넣기 (~22k 토큰, 그림 제외). `scripts/build_review_packet.py` 가 자동 생성. |
| [`CLAIMS_LEDGER.md`](CLAIMS_LEDGER.md) | 본 리포가 한 **36개 검증 가능한 주장에 번호 + 증거 파일 링크**. 한 줄씩 검증할 수 있도록 정리. |
| [`REVIEW_PROMPTS.md`](REVIEW_PROMPTS.md) | **6종 미리 작성된 리뷰 프롬프트** (통합 / Falsification / 방법론 / 통계 / 도메인 / 재현성). 모델에 그대로 붙여넣기 |
| [`key_results.json`](key_results.json) | 핵심 수치를 구조화된 JSON 으로. 모델이 수치 검증 시 사용 |

---

## 🚀 빠른 시작 — 외부 모델 리뷰 5분 가이드

### 옵션 A. "최고 컨텍스트 모델로 한방에 검증"

추천 모델: GPT-5.5 Pro (200K), Claude Opus 4.7 (1M), Gemini 2.5 Pro (2M)

```
1. REVIEW_PACKET.md 를 통째로 모델에 첨부 (또는 paste)
2. REVIEW_PROMPTS.md 의 "통합 리뷰" 프롬프트를 사용
3. 응답을 issue 로 공유 (라벨: external-review)
```

### 옵션 B. "분야별 전문 리뷰"

```
1. REVIEW_PACKET.md 첨부
2. REVIEW_PROMPTS.md 의 6종 중 관심 분야 선택:
   - 통합 리뷰 (모든 측면 한번에)
   - Falsification (가장 강한 비판 유도 — 결론 무너뜨릴 falsification test 요구)
   - 방법론 (CMI, PC, decoupling probe 의 적용이 정확한가)
   - 통계 (임계, 표본 크기, 효과크기 해석이 적절한가)
   - 도메인 (한국 인구통계 해석이 맞는가)
   - 재현성 (코드/수치를 제3자가 검증 가능한가)
3. 별도 호출 → 분야별 리포트 받기
```

### 옵션 C. "수치 검증만 빠르게"

```
1. key_results.json 을 모델에 줌
2. "이 JSON 의 핵심 수치 12개를 1개씩 검증하라.
    각각 (a) 수치가 합리적인가, (b) 사용된 방법론이 적절한가, (c) 의심 사항을 적어라"
```

---

## 🔧 패키지 빌드

```bash
python scripts/build_review_packet.py
```

이 명령은 다음을 자동 수집해 `review/REVIEW_PACKET.md` 와 `review/key_results.json` 을 갱신:
- 본문: `reports/PHASE1~3_REPORT.md`, `CLAIMS_LEDGER.md`, `docs/METHODOLOGY.md`
- 수치: `data/processed/marginals_summary.json`, `kosis_comparison.json`, `cmi/skeleton.json`, `cmi/stability.csv`, `cmi/node_degrees.csv`, `decoupling_probe.json`, `bivariate/metrics_long.csv`
- 외부 reference: `data/reference/kosis_reference.json`

분석을 수정한 뒤에는 빌더를 다시 돌려 패키지를 동기화하세요.

---

## 📝 결과 공유

외부 리뷰 결과는 GitHub issue (`external-review` 라벨) 로 공유 부탁드립니다.
issue 템플릿: [`.github/ISSUE_TEMPLATE/external_review.md`](../.github/ISSUE_TEMPLATE/external_review.md)

가장 가치 있는 리뷰는:
1. 본 리포의 **결론을 정정**하는 리뷰
2. 본 리포가 **놓친 분석 각도**를 제안하는 리뷰
3. **수치 오류**를 잡아내는 리뷰
