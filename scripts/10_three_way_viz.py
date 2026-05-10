"""3-way visualizations for the most consequential decoupling hypotheses.

Each figure: P(target = level | X, Y) shown as a heatmap (rows = X, cols = Y).
'Flat' heatmap → target is conditionally independent of (X,Y) given current model
'Patterned' heatmap → there's signal in the joint that PGM has captured (or not).

Plotted:
  A. P(아파트 | age, marital_status)           — does PGM tie housing to person attrs?
  B. P(혼자 거주 | age, marital_status)        — sanity: 미혼/사별 → 1인가구
  C. P(현역 | sex, age)                        — military realism check
  D. P(무직 | age, education_level)            — retirement / low-edu → unemployed
  E. P(아파트 | district[top10], age_bin)      — within-district age effect on housing?
  F. P(배우자있음 | age, sex)                  — age/sex interaction on marriage
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import AGE_LABELS, ROOT, load_df, setup_korean_font

FIG_DIR = ROOT / "reports" / "figures" / "threeway"
FIG_DIR.mkdir(parents=True, exist_ok=True)
setup_korean_font()


def conditional_rate(df: pl.DataFrame, target_col: str, target_value: str,
                     x: str, y: str,
                     x_order: list[str] | None = None,
                     y_order: list[str] | None = None,
                     min_n: int = 30):
    """Returns (rate_matrix, n_matrix, x_labels, y_labels)."""
    work = df.with_columns(
        (pl.col(target_col) == target_value).cast(pl.Int8).alias("__t__")
    )
    g = (
        work.group_by([x, y])
        .agg([pl.len().alias("n"), pl.col("__t__").sum().alias("k")])
        .to_pandas()
    )
    if x_order is None:
        x_order = sorted(g[x].unique())
    if y_order is None:
        y_order = sorted(g[y].unique())

    rate = np.full((len(x_order), len(y_order)), np.nan)
    nn = np.zeros_like(rate)
    for r in g.itertuples():
        xv, yv = getattr(r, x), getattr(r, y)
        if xv not in x_order or yv not in y_order:
            continue
        i, j = x_order.index(xv), y_order.index(yv)
        nn[i, j] = r.n
        if r.n >= min_n:
            rate[i, j] = r.k / r.n
    return rate, nn, x_order, y_order


def heatmap(rate, nn, x_labels, y_labels, title, fname,
            vmin=None, vmax=None, fmt="{:.0%}"):
    fig, ax = plt.subplots(figsize=(max(6, 0.45 * len(y_labels) + 4),
                                    max(4, 0.4 * len(x_labels) + 2)))
    im = ax.imshow(rate, cmap="magma", aspect="auto", vmin=vmin, vmax=vmax)
    ax.set_xticks(range(len(y_labels)))
    ax.set_xticklabels(y_labels, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(x_labels)))
    ax.set_yticklabels(x_labels, fontsize=9)
    for i in range(len(x_labels)):
        for j in range(len(y_labels)):
            v = rate[i, j]
            if np.isnan(v):
                ax.text(j, i, "—", ha="center", va="center", color="#888", fontsize=8)
                continue
            text_color = "white" if v < (vmax or 1) * 0.55 else "black"
            label = fmt.format(v)
            sub = f"\n(n={int(nn[i,j]):,})"
            ax.text(j, i, label + sub, ha="center", va="center",
                    color=text_color, fontsize=7)
    ax.set_title(title, fontsize=11)
    fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    fig.tight_layout()
    fig.savefig(fname, dpi=130)
    plt.close(fig)


def main() -> None:
    df = load_df()
    print(f"rows = {df.height:,}")
    MARITAL_ORDER = ["미혼", "배우자있음", "사별", "이혼"]

    # A. P(아파트 | age, marital) — housing decoupling test
    rate, nn, xs, ys = conditional_rate(df, "housing_type", "아파트",
                                        "age_bin", "marital_status",
                                        x_order=AGE_LABELS, y_order=MARITAL_ORDER)
    heatmap(rate, nn, xs, ys,
            "(A) P(아파트 | 연령, 혼인상태)\n"
            "현실: 1인가구·청년·미혼은 작은 다세대/오피스텔 비중 ↑   "
            "→ 만일 PGM이 housing을 사람 속성과 묶었다면 매트릭스가 패턴을 가져야 함",
            FIG_DIR / "A_apt_by_age_marital.png", vmin=0.55, vmax=0.7)

    # B. P(혼자 거주 | age, marital) — sanity: PGM should connect these
    rate, nn, xs, ys = conditional_rate(df, "family_type", "혼자 거주",
                                        "age_bin", "marital_status",
                                        x_order=AGE_LABELS, y_order=MARITAL_ORDER)
    heatmap(rate, nn, xs, ys,
            "(B) P(혼자 거주 | 연령, 혼인상태)\n"
            "현실: 미혼/사별·고연령에서 매우 높음   "
            "→ PGM이 marital→family를 잘 잡았다면 강한 패턴이 보여야 함",
            FIG_DIR / "B_alone_by_age_marital.png", vmin=0, vmax=1)

    # C. P(현역 | sex, age) — military realism
    rate, nn, xs, ys = conditional_rate(df, "military_status", "현역",
                                        "sex", "age_bin",
                                        x_order=["남자", "여자"], y_order=AGE_LABELS)
    heatmap(rate, nn, xs, ys,
            "(C) P(현역 | 성별, 연령)\n"
            "주의: 현역 = 직업군인(부사관·장교, 11% 여성) + 의무복무 사병 통합 라벨. "
            "병사는 19-30 남성, 부사관·장교는 정년(55-63)까지 → 자연스러운 분포",
            FIG_DIR / "C_active_by_sex_age.png", vmin=0, vmax=0.025,
            fmt="{:.2%}")

    # D. P(무직 | age, education)
    EDU_ORDER = ["무학", "초등학교", "중학교", "고등학교",
                 "2~3년제 전문대학", "4년제 대학교", "대학원"]
    rate, nn, xs, ys = conditional_rate(df, "occupation", "무직",
                                        "age_bin", "education_level",
                                        x_order=AGE_LABELS, y_order=EDU_ORDER)
    heatmap(rate, nn, xs, ys,
            "(D) P(무직 | 연령, 학력)\n"
            "현실: 노년·저학력에서 ↑, 35-54·고학력에서 ↓",
            FIG_DIR / "D_jobless_by_age_edu.png", vmin=0, vmax=1)

    # E. P(아파트 | top-10 district, age) — within-district age effect
    top_districts = (
        df.group_by("district").agg(pl.len().alias("n"))
        .sort("n", descending=True).head(10)["district"].to_list()
    )
    sub = df.filter(pl.col("district").is_in(top_districts))
    rate, nn, xs, ys = conditional_rate(sub, "housing_type", "아파트",
                                        "district", "age_bin",
                                        x_order=top_districts, y_order=AGE_LABELS,
                                        min_n=50)
    heatmap(rate, nn, xs, ys,
            "(E) P(아파트 | district[top10], 연령)\n"
            "도시 통제 후에도 연령에 따라 변동이 있는가? "
            "→ 거의 평탄이면 housing이 district 외 person-attrs와 독립",
            FIG_DIR / "E_apt_by_district_age.png", vmin=0.3, vmax=1)

    # F. P(배우자있음 | age, sex) — age × sex interaction on marriage
    rate, nn, xs, ys = conditional_rate(df, "marital_status", "배우자있음",
                                        "age_bin", "sex",
                                        x_order=AGE_LABELS, y_order=["남자", "여자"])
    heatmap(rate, nn, xs, ys,
            "(F) P(배우자있음 | 연령, 성별)\n"
            "현실: 고령 여성은 사별로 배우자있음 비율 급락",
            FIG_DIR / "F_married_by_age_sex.png", vmin=0, vmax=1)

    print(f"Wrote 6 figures to {FIG_DIR}")


if __name__ == "__main__":
    main()
