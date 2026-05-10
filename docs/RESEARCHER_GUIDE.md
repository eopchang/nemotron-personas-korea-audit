# 연구자 사용 가이드

> "내 연구에 Nemotron-Personas-Korea를 써도 될까?" 결정하는 데 필요한 짧은 체크리스트.

---

## 🟢 사용 가능 (충실도 검증됨)

### 인구통계 시뮬레이션
- 시도/시군구별 인구 분포 (TVD = 0.005, ±0.24pp 이내)
- 성별·연령 인구 피라미드 (85+ 여성 71%, 19-24 여성 47.6% — 한국 현실 일치)

### 인구학적 chain 분석
- `age × marital × family_type` — 25-34 미혼 65%, 75-84 사별 43% 등 한국 패턴과 부합
- `age × education_level` — 코호트 효과 (85+ 무학+초등 76%) 잘 잡힘
- `age × occupation` — 은퇴/재직 패턴

### 교육-노동 분리 연구
- `bachelors_field × sex × occupation` — 공학 86% 남성, 보건 28% 남성 등 한국 노동시장 분리 패턴과 부합

### LLM 학습 / 페르소나 텍스트 생성
- 데이터셋 본래 용도. 텍스트 다양성·자연스러움 우수.
- 한국어 LLM 의 "한국적 인물" 표현 능력 향상에 적합.

### 합성 데이터 평가 방법론 강의 / 사례 연구
- 본 리포 그림 자체가 합성 데이터 검증의 좋은 사례.

---

## ⚠️ 사용 부적합 (구조적 한계 확인됨)

### 주거 정책 / 주거 빈곤 연구 ❌
- **이유**: housing_type 이 사람 속성과 통계적으로 분리됨 (decoupling probe info_added = −0.008 nats).
- **증상**: 1인 가구도, 4인 가족도, 청년도 노년도 모두 아파트 ~61%. 현실의 주거 다양성 미반영.
- **대안**: KOSIS 인구주택총조사 미시 자료, 한국주거실태조사

### 의무복무 흐름·동학 분석 ❌
- **이유**: military_status 는 정적 cross-section 라벨. 입영·전역 시점, 복무 길이 (1년/1.5년/2년) 등 dynamic 정보 없음.
- **대안**: 병무청 통계연보, 국방부 발간 자료

### 현역 군 인력 구성 분석 🤔 (가능하지만 주의)
- **사용 가능**: 계급별 연령·성비 cross-section. 한국군 현실 부합 (`data/processed/military_breakdown.json`).
- **주의**: military_status 가 occupation 에서 거의 결정됨 → 두 변수를 동시에 모델 입력으로 쓰면 정보 중복.
- **변수 의미**: '현역' = 직업군인 (부사관·장교) + 의무복무 사병 통합. 미국식 "active duty" 에 더 가까움.

### 지역별 사람 속성 미세 분석 ❌
- **이유**: housing 외에는 지리(province·district)와 사람 속성의 결합이 약하게만 모델링됨. 시도별 직업 분포 차이 등은 KOSIS reference 보다 약함.
- **대안**: 통계청 지역별 고용조사, 각 지자체 통계연보

### 1인 가구 vs 다인 가구의 *주거·소비* 차이 분석 ❌
- **이유**: 위 housing decoupling 의 직접 결과 (개인 속성에 따른 주거 형태 차이가 미반영). 단 "지역별 주택 유형 분포" 같은 시군구 단위 시뮬레이션은 별도.
- **대안**: 통계청 1인가구 사회조사

### 시계열 / 생애주기 분석 ❌
- **이유**: 정적 스냅샷 (2024년 시드). 동적 경로 정보 없음. 데이터 카드 자체가 "시간성 부재" 를 한계로 명시.

### "의무복무 흐름이 직업·결혼에 미치는 영향" 같은 동학 분석 ❌
- **이유**: military_status 가 정적 cross-section 라벨이라 입영·전역 흐름 정보 없음. occupation 과 거의 결정적으로 결합되어 분리된 inference 불가.
- **참고**: 현역 인력의 cross-section 구성 (계급별 연령·성비 등) 분석은 가능 — 위 § "현역 군 인력 구성 분석" 참조.

---

## 🤔 신중하게 사용

### 직업 분포 분석
- ✅ 큰 그림 (전체 직업 분포, 무직 36.7%) 은 KOSIS 와 부합
- ⚠️ 미시: 직업명 2,120개 중 분류 체계가 KSCO 와 일대일 매핑되지 않음. KSCO 분류로 변환하려면 별도 작업 필요.

### 결혼·가족 분석
- ✅ 결혼 상태 → 가족 유형의 결정론적 일관성 100% (단, 별거·주말부부·기러기 가족 등 현실 다양성은 일부 제거)
- ⚠️ "혼자 거주" 비율은 약 14% (개인 단위) — 통계청 2023 1인가구 비율 약 35% 는 *가구 단위* 이므로 직접 비교 불가. 가구 단위 1인가구 비율과 개인 단위 혼자 사는 사람 비율은 다른 지표 (1인가구는 가구 수로는 많지만 가구당 사람이 1명뿐). 본 데이터의 14% 가 적절한 개인 단위 reference 와 부합하는지 별도 검증 필요.

### 학력 분포 분석
- ✅ 7개 카테고리, 코호트 효과 잘 반영
- ⚠️ 25세+ vs 19세+ 모집단 차이로 인한 4년제 비중이 약간 상향 편향 가능 (PHASE1_REPORT §3-2)

### 농촌 / 도시 비교
- ✅ province × housing 결합은 도시 단독↓ / 농촌 단독↑ 패턴 잘 잡음
- ⚠️ 그러나 housing 의 *전체* 분포가 어긋나 있어 (아파트 +9pp 과대) 비교 baseline으로 쓰기 위험

---

## 빠른 결정 흐름

```
질문: 내가 분석하려는 변수에 housing_type 이 들어가는가?
  → 예: 사람 속성 (age/marital/family/edu/occ) 과 housing 의 결합이 핵심?
        → 예: ❌ 부적합
        → 아니오 (지역 단위 housing 만): 🤔 신중
  → 아니오: 다음 질문

질문: military_status 가 분석 변수인가?
  → 예, 의무복무 흐름·동학이 핵심: ❌ 부적합
  → 예, 현역 인력 cross-section 구성만: 🤔 가능. 단 occupation과 정보 중복 주의
  → 아니오: 다음 질문

질문: 분석에 시계열·생애주기 정보가 필요한가?
  → 예: ❌ 부적합
  → 아니오: 다음 질문

질문: 변수 = {age, sex, marital, family, education, bachelors_field, occupation, district, province} 중에서 고르며,
       각 변수의 marginal 그리고 1차 결합이 충실하면 충분한가?
  → 예: 🟢 사용 가능
  → 아니오 (3차 이상 결합 정확성, 미세 effect 필요): 🤔 본 리포 결과를 보고 개별 판단
```

---

## 보완 데이터 출처

| 본 데이터에 부족한 부분 | 보완 자료 |
|---|---|
| 주거 (가구 단위) | [KOSIS 인구주택총조사](https://kosis.kr/) |
| 주거 (개인 단위 행태) | [국토부 주거실태조사](https://stat.molit.go.kr) |
| 병역 / 군 인구 | [병무청 통계연보](https://www.mma.go.kr) |
| 직업 (KSCO 미세 분류) | [통계청 지역별 고용조사](https://kosis.kr/) |
| 1인 가구 사회상 | [통계청 1인가구 사회조사](https://kosis.kr/) |
| 학력 코호트 | [교육부 교육기본통계](https://kess.kedi.re.kr/) |

---

## 인용 시 권장 표현

> "Synthetic personas were drawn from `nvidia/Nemotron-Personas-Korea` (CC BY 4.0).
> Following the audit by Kim (2026)\*, we restrict our use to {age, sex, marital, family,
> education, bachelors_field, occupation, district, province} as the dataset's
> housing_type and military_status variables show structural decoupling
> from person attributes."
>
> \*Kim, C.-E. (2026). *Nemotron-Personas-Korea Audit: Independent Statistical
> Audit of NVIDIA's Korean Synthetic Persona Dataset*. https://github.com/eopchang/nemotron-personas-korea-audit
