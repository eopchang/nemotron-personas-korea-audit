# 기여 가이드

이 리포에 기여를 환영합니다. 본 프로젝트는 **데이터 독립 검토** 이므로,
새로운 기능보다는 **검증 강화 / 방법론 수정 / 결과 반박** 이 더 환영받습니다.

## 기여 방향

### 환영합니다
- **방법론 검증**: CMI 임계 ε, PC-style |Z| 한계 등에 대한 도전·개선 ([ROADMAP.md](ROADMAP.md) P3, P4)
- **외부 reference 보강**: KOSIS 원시 표·미시 자료 기반 더 정밀한 비교 ([ROADMAP.md](ROADMAP.md) P7)
- **새로운 분석**: 3-way 이상의 결합, 텍스트 페르소나 분석 ([ROADMAP.md](ROADMAP.md) P9)
- **결과 반박**: 우리 결론이 틀렸음을 보이는 데이터·코드. 
- **다른 LLM/모델로 외부 리뷰**: 결과를 [`review/`](review/) 의 packet으로 점검

## 시작하기

1. issue 먼저 — 큰 작업 전에 [이슈](https://github.com/eopchang/nemotron-personas-korea-audit/issues)에서 논의
2. fork → branch → PR
3. `python scripts/0[1-9]_*.py` 가 모두 통과해야 함
4. 새 분석 추가 시 `reports/` 에 결과를 추가하고 README와 PHASE 리포트 업데이트

## 코드 스타일

- Python 3.12, ruff/black 권장 
- 함수에 docstring, 모듈 상단에 무엇을 하는지 한 문단 요약
- 모든 산출물 파일 경로는 `scripts/_lib.py:ROOT` 기준

## 외부 모델 리뷰 결과를 공유하고 싶다면

[`review/`](review/) 디렉토리의 `REVIEW_PROMPTS.md` 를 사용해 GPT / Claude / Gemini
등 최신 모델로 검증한 결과를 issue로 남겨주세요. 라벨 `external-review`.

## 행동 강령

서로 존중. NVIDIA 연구자가 본 결과를 정정하거나 보강한다면 환영합니다.
이 검토는 NVIDIA를 비판하는 것이 목적이 아니라 **이 데이터셋의 적절한 사용 범위**
를 사용자가 판단할 수 있도록 돕는 것이 목적입니다.
