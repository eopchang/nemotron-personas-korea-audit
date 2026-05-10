"""Build a navigable markdown gallery for all 55 pair-detail figures, sorted by NMI."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
IDX = ROOT / "data" / "processed" / "bivariate_detail_all" / "index.csv"
OUT = ROOT / "reports" / "PAIR_INDEX.md"


def main() -> None:
    df = pd.read_csv(IDX).sort_values("NMI", ascending=False).reset_index(drop=True)
    lines = ["# 모든 11C2 = 55 페어의 detail 색인", "",
             "(NMI 내림차순. 각 항목 클릭 시 3-panel 그림으로 이동.)",
             "",
             "| # | x | y | V | NMI | U(Y\\|X) | U(X\\|Y) | TVD_indep | trunc | link |",
             "|---:|---|---|---:|---:|---:|---:|---:|---|---|"]
    for i, r in df.iterrows():
        trunc = []
        if pd.notna(r["x_truncated_to"]):
            trunc.append(f"x→top{int(r['x_truncated_to'])}")
        if pd.notna(r["y_truncated_to"]):
            trunc.append(f"y→top{int(r['y_truncated_to'])}")
        trunc_s = ", ".join(trunc) if trunc else "—"
        link = f"[fig](figures/bivariate_all/{r['x']}__x__{r['y']}.png)"
        lines.append(
            f"| {i+1} | `{r['x']}` | `{r['y']}` | "
            f"{r['V']:.3f} | {r['NMI']:.3f} | {r['U_y_given_x']:.3f} | "
            f"{r['U_x_given_y']:.3f} | {r['TVD_indep']:.3f} | {trunc_s} | {link} |"
        )
    lines += ["", "## 보조 자료",
              "- 4 association heatmaps: `reports/figures/heatmap_*.png`",
              "- Per-pair raw tables: `data/processed/bivariate_detail_all/contingency_*.csv`, `cells_*.csv`",
              "- Long-form metrics: `data/processed/bivariate/metrics_long.csv`"]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
