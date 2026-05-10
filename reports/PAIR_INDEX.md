# 모든 11C2 = 55 페어의 detail 색인

(NMI 내림차순. 각 항목 클릭 시 3-panel 그림으로 이동.)

| # | x | y | V | NMI | U(Y\|X) | U(X\|Y) | TVD_indep | trunc | link |
|---:|---|---|---:|---:|---:|---:|---:|---|---|
| 1 | `district` | `province` | 1.000 | 0.635 | 1.000 | 0.465 | 0.872 | x→top25 | [fig](figures/bivariate_all/district__x__province.png) |
| 2 | `marital_status` | `family_type` | 0.694 | 0.440 | 0.317 | 0.717 | 0.494 | y→top15 | [fig](figures/bivariate_all/marital_status__x__family_type.png) |
| 3 | `education_level` | `bachelors_field` | 0.408 | 0.421 | 0.476 | 0.377 | 0.439 | — | [fig](figures/bivariate_all/education_level__x__bachelors_field.png) |
| 4 | `age_bin` | `marital_status` | 0.483 | 0.210 | 0.301 | 0.162 | 0.283 | — | [fig](figures/bivariate_all/age_bin__x__marital_status.png) |
| 5 | `age_bin` | `family_type` | 0.337 | 0.153 | 0.140 | 0.169 | 0.309 | y→top15 | [fig](figures/bivariate_all/age_bin__x__family_type.png) |
| 6 | `age_bin` | `education_level` | 0.333 | 0.152 | 0.165 | 0.141 | 0.281 | — | [fig](figures/bivariate_all/age_bin__x__education_level.png) |
| 7 | `education_level` | `occupation` | 0.333 | 0.104 | 0.072 | 0.188 | 0.288 | y→top20 | [fig](figures/bivariate_all/education_level__x__occupation.png) |
| 8 | `bachelors_field` | `occupation` | 0.261 | 0.083 | 0.054 | 0.177 | 0.220 | y→top20 | [fig](figures/bivariate_all/bachelors_field__x__occupation.png) |
| 9 | `marital_status` | `education_level` | 0.288 | 0.077 | 0.063 | 0.100 | 0.146 | — | [fig](figures/bivariate_all/marital_status__x__education_level.png) |
| 10 | `age_bin` | `occupation` | 0.210 | 0.053 | 0.038 | 0.085 | 0.230 | y→top20 | [fig](figures/bivariate_all/age_bin__x__occupation.png) |
| 11 | `housing_type` | `district` | 0.266 | 0.049 | 0.030 | 0.135 | 0.194 | y→top25 | [fig](figures/bivariate_all/housing_type__x__district.png) |
| 12 | `sex` | `occupation` | 0.454 | 0.046 | 0.027 | 0.169 | 0.186 | y→top20 | [fig](figures/bivariate_all/sex__x__occupation.png) |
| 13 | `family_type` | `education_level` | 0.183 | 0.045 | 0.054 | 0.038 | 0.144 | x→top15 | [fig](figures/bivariate_all/family_type__x__education_level.png) |
| 14 | `housing_type` | `province` | 0.176 | 0.042 | 0.031 | 0.065 | 0.130 | — | [fig](figures/bivariate_all/housing_type__x__province.png) |
| 15 | `occupation` | `district` | 0.051 | 0.040 | 0.037 | 0.044 | 0.171 | x→top20, y→top25 | [fig](figures/bivariate_all/occupation__x__district.png) |
| 16 | `age_bin` | `bachelors_field` | 0.133 | 0.040 | 0.049 | 0.033 | 0.138 | — | [fig](figures/bivariate_all/age_bin__x__bachelors_field.png) |
| 17 | `sex` | `bachelors_field` | 0.264 | 0.037 | 0.028 | 0.054 | 0.087 | — | [fig](figures/bivariate_all/sex__x__bachelors_field.png) |
| 18 | `sex` | `marital_status` | 0.227 | 0.032 | 0.027 | 0.040 | 0.063 | — | [fig](figures/bivariate_all/sex__x__marital_status.png) |
| 19 | `marital_status` | `bachelors_field` | 0.123 | 0.021 | 0.019 | 0.024 | 0.071 | — | [fig](figures/bivariate_all/marital_status__x__bachelors_field.png) |
| 20 | `family_type` | `occupation` | 0.066 | 0.021 | 0.016 | 0.029 | 0.131 | x→top15, y→top20 | [fig](figures/bivariate_all/family_type__x__occupation.png) |
| 21 | `marital_status` | `occupation` | 0.178 | 0.018 | 0.011 | 0.048 | 0.097 | y→top20 | [fig](figures/bivariate_all/marital_status__x__occupation.png) |
| 22 | `education_level` | `district` | 0.140 | 0.015 | 0.010 | 0.031 | 0.112 | y→top25 | [fig](figures/bivariate_all/education_level__x__district.png) |
| 23 | `military_status` | `occupation` | 1.000 | 0.015 | 0.008 | 1.000 | 0.011 | y→top20 | [fig](figures/bivariate_all/military_status__x__occupation.png) |
| 24 | `occupation` | `province` | 0.083 | 0.014 | 0.020 | 0.011 | 0.089 | x→top20 | [fig](figures/bivariate_all/occupation__x__province.png) |
| 25 | `family_type` | `district` | 0.064 | 0.013 | 0.009 | 0.021 | 0.102 | x→top15, y→top25 | [fig](figures/bivariate_all/family_type__x__district.png) |
| 26 | `sex` | `education_level` | 0.162 | 0.012 | 0.008 | 0.020 | 0.051 | — | [fig](figures/bivariate_all/sex__x__education_level.png) |
| 27 | `sex` | `family_type` | 0.181 | 0.011 | 0.007 | 0.025 | 0.051 | y→top15 | [fig](figures/bivariate_all/sex__x__family_type.png) |
| 28 | `family_type` | `bachelors_field` | 0.060 | 0.010 | 0.014 | 0.008 | 0.072 | x→top15 | [fig](figures/bivariate_all/family_type__x__bachelors_field.png) |
| 29 | `bachelors_field` | `district` | 0.079 | 0.009 | 0.006 | 0.023 | 0.089 | y→top25 | [fig](figures/bivariate_all/bachelors_field__x__district.png) |
| 30 | `education_level` | `province` | 0.079 | 0.009 | 0.007 | 0.011 | 0.068 | — | [fig](figures/bivariate_all/education_level__x__province.png) |
| 31 | `family_type` | `province` | 0.055 | 0.008 | 0.007 | 0.008 | 0.065 | x→top15 | [fig](figures/bivariate_all/family_type__x__province.png) |
| 32 | `bachelors_field` | `province` | 0.049 | 0.006 | 0.005 | 0.009 | 0.058 | — | [fig](figures/bivariate_all/bachelors_field__x__province.png) |
| 33 | `age_bin` | `district` | 0.080 | 0.006 | 0.004 | 0.011 | 0.073 | y→top25 | [fig](figures/bivariate_all/age_bin__x__district.png) |
| 34 | `sex` | `military_status` | 0.059 | 0.006 | 0.061 | 0.003 | 0.004 | — | [fig](figures/bivariate_all/sex__x__military_status.png) |
| 35 | `marital_status` | `district` | 0.108 | 0.005 | 0.003 | 0.015 | 0.055 | y→top25 | [fig](figures/bivariate_all/marital_status__x__district.png) |
| 36 | `marital_status` | `province` | 0.067 | 0.004 | 0.003 | 0.006 | 0.038 | — | [fig](figures/bivariate_all/marital_status__x__province.png) |
| 37 | `housing_type` | `occupation` | 0.065 | 0.004 | 0.002 | 0.008 | 0.033 | y→top20 | [fig](figures/bivariate_all/housing_type__x__occupation.png) |
| 38 | `age_bin` | `province` | 0.045 | 0.003 | 0.003 | 0.004 | 0.046 | — | [fig](figures/bivariate_all/age_bin__x__province.png) |
| 39 | `housing_type` | `education_level` | 0.042 | 0.003 | 0.002 | 0.004 | 0.026 | — | [fig](figures/bivariate_all/housing_type__x__education_level.png) |
| 40 | `age_bin` | `sex` | 0.080 | 0.002 | 0.005 | 0.002 | 0.024 | — | [fig](figures/bivariate_all/age_bin__x__sex.png) |
| 41 | `age_bin` | `housing_type` | 0.032 | 0.002 | 0.002 | 0.001 | 0.024 | — | [fig](figures/bivariate_all/age_bin__x__housing_type.png) |
| 42 | `age_bin` | `military_status` | 0.046 | 0.002 | 0.048 | 0.001 | 0.003 | — | [fig](figures/bivariate_all/age_bin__x__military_status.png) |
| 43 | `housing_type` | `bachelors_field` | 0.028 | 0.002 | 0.001 | 0.002 | 0.022 | — | [fig](figures/bivariate_all/housing_type__x__bachelors_field.png) |
| 44 | `family_type` | `housing_type` | 0.029 | 0.001 | 0.002 | 0.001 | 0.022 | x→top15 | [fig](figures/bivariate_all/family_type__x__housing_type.png) |
| 45 | `marital_status` | `housing_type` | 0.030 | 0.001 | 0.001 | 0.001 | 0.013 | — | [fig](figures/bivariate_all/marital_status__x__housing_type.png) |
| 46 | `marital_status` | `military_status` | 0.031 | 0.001 | 0.016 | 0.001 | 0.002 | — | [fig](figures/bivariate_all/marital_status__x__military_status.png) |
| 47 | `military_status` | `education_level` | 0.032 | 0.001 | 0.000 | 0.021 | 0.002 | — | [fig](figures/bivariate_all/military_status__x__education_level.png) |
| 48 | `military_status` | `bachelors_field` | 0.029 | 0.001 | 0.000 | 0.010 | 0.002 | — | [fig](figures/bivariate_all/military_status__x__bachelors_field.png) |
| 49 | `military_status` | `family_type` | 0.029 | 0.000 | 0.000 | 0.014 | 0.002 | y→top15 | [fig](figures/bivariate_all/military_status__x__family_type.png) |
| 50 | `sex` | `district` | 0.036 | 0.000 | 0.000 | 0.001 | 0.015 | y→top25 | [fig](figures/bivariate_all/sex__x__district.png) |
| 51 | `military_status` | `district` | 0.039 | 0.000 | 0.000 | 0.017 | 0.002 | y→top25 | [fig](figures/bivariate_all/military_status__x__district.png) |
| 52 | `military_status` | `province` | 0.023 | 0.000 | 0.000 | 0.006 | 0.001 | — | [fig](figures/bivariate_all/military_status__x__province.png) |
| 53 | `sex` | `province` | 0.020 | 0.000 | 0.000 | 0.000 | 0.009 | — | [fig](figures/bivariate_all/sex__x__province.png) |
| 54 | `military_status` | `housing_type` | 0.006 | 0.000 | 0.000 | 0.001 | 0.000 | — | [fig](figures/bivariate_all/military_status__x__housing_type.png) |
| 55 | `sex` | `housing_type` | 0.005 | 0.000 | 0.000 | 0.000 | 0.002 | — | [fig](figures/bivariate_all/sex__x__housing_type.png) |

## 보조 자료
- 4 association heatmaps: `reports/figures/heatmap_*.png`
- Per-pair raw tables: `data/processed/bivariate_detail_all/contingency_*.csv`, `cells_*.csv`
- Long-form metrics: `data/processed/bivariate/metrics_long.csv`