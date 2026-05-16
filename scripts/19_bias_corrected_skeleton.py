"""Bias-corrected skeleton diagram (P4 permutation null applied).

Replaces the binary 'direct vs not' view in skeleton_network.png with a 3-tier
visualization that distinguishes:
  ★★★ robust  (ratio_obs/null_p95 >= 10) — strong signal far above bias floor
  ★★  signif (ratio 2-10)               — significant but not overwhelming
  ⚠️  suspect (ratio < 2)                 — bias-suspect, may not be a real edge

Edge thickness = log-scaled with ratio. Suspect edges drawn dashed/thin to
visually de-emphasize.

Output: reports/figures/skeleton_bias_corrected.png
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import ROOT, setup_korean_font

setup_korean_font()
OUT = ROOT / "reports" / "figures" / "skeleton_bias_corrected.png"

POS = {
    "age_bin":         (-0.8, 1.4),
    "sex":             ( 1.0, 1.4),
    "province":        (-2.6, 0.2),
    "district":        (-2.6,-0.5),
    "housing_type":    (-2.6,-1.5),
    "education_level": (-1.1, 0.0),
    "bachelors_field": (-0.5,-0.8),
    "marital_status":  ( 0.4, 0.0),
    "family_type":     ( 2.2,-0.6),
    "occupation":      (-0.1,-1.5),
    "military_status": ( 1.6,-1.5),
}

# Display labels (shorter, fit inside nodes)
LABEL = {
    "age_bin":         "age",
    "sex":             "sex",
    "province":        "province",
    "district":        "district",
    "housing_type":    "housing",
    "education_level": "education",
    "bachelors_field": "bachelors",
    "marital_status":  "marital",
    "family_type":     "family",
    "occupation":      "occupation",
    "military_status": "military",
}

NODE_GROUP = {
    "province": "geo", "district": "geo", "housing_type": "geo",
    "age_bin": "demo", "sex": "demo",
    "education_level": "edu", "bachelors_field": "edu",
    "marital_status": "fam", "family_type": "fam",
    "occupation": "outcome", "military_status": "outcome",
}
GROUP_COLOR = {"geo": "#a5cce6", "demo": "#ffd180", "edu": "#b9e3c7",
               "fam": "#f4c2c2", "outcome": "#e0d4f7"}

TIER = {
    "robust":  {"color": "#0a2e5c", "alpha": 0.95, "style": "solid",  "min_w": 3.0},
    "signif":  {"color": "#3a78c2", "alpha": 0.85, "style": "solid",  "min_w": 1.8},
    "suspect": {"color": "#c0392b", "alpha": 0.55, "style": "dashed", "min_w": 0.7},
}


def classify(ratio: float) -> str:
    if ratio >= 10:
        return "robust"
    if ratio >= 2:
        return "signif"
    return "suspect"


def edge_width(ratio: float, tier: str) -> float:
    base = TIER[tier]["min_w"]
    return base + min(4.0, math.log10(max(ratio, 1.01)) * 1.8)


def main() -> None:
    skel = pd.read_csv(ROOT / "data/processed/cmi/skeleton.csv")
    perm = pd.read_csv(ROOT / "data/processed/cmi/permutation_null_conditional.csv")
    direct = (
        skel[skel.edge_class == "direct"][["x", "y", "mi_xy", "cmi_min_any"]]
        .merge(perm[["x", "y", "observed", "null_p95", "ratio_obs_to_p95"]],
               on=["x", "y"])
    )
    direct["tier"] = direct["ratio_obs_to_p95"].apply(classify)
    counts = direct["tier"].value_counts().to_dict()

    G = nx.Graph()
    for n in POS:
        G.add_node(n)
    for r in direct.itertuples():
        G.add_edge(r.x, r.y, ratio=r.ratio_obs_to_p95, tier=r.tier,
                   observed=r.observed, null_p95=r.null_p95)

    # ===== two-panel layout: network (robust+signif only) + ratio bar =====
    fig = plt.figure(figsize=(17, 9))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 0.85], wspace=0.30)
    ax_net = fig.add_subplot(gs[0, 0])
    ax_bar = fig.add_subplot(gs[0, 1])

    n_robust = counts.get("robust", 0); n_signif = counts.get("signif", 0)
    n_suspect = counts.get("suspect", 0)

    # --- (A) Network: robust + significant only ---
    nx.draw_networkx_nodes(G, POS, node_size=3400,
                           node_color=[GROUP_COLOR[NODE_GROUP[n]] for n in G.nodes],
                           edgecolors="black", linewidths=1.3, ax=ax_net)
    nx.draw_networkx_labels(G, POS, labels=LABEL, font_size=10,
                            font_family=plt.rcParams["font.family"], ax=ax_net)
    for tier in ["signif", "robust"]:
        edges = [(u, v) for u, v, d in G.edges(data=True) if d["tier"] == tier]
        widths = [edge_width(G[u][v]["ratio"], tier) for u, v in edges]
        nx.draw_networkx_edges(
            G, POS, edgelist=edges,
            edge_color=TIER[tier]["color"], style=TIER[tier]["style"],
            width=widths, alpha=TIER[tier]["alpha"],
            node_size=3400, ax=ax_net,
        )
    # Label only the TOP-N edges by ratio to keep the network uncluttered.
    # The ranked bar chart on the right shows ALL ratios.
    LABELED_TOP_N = 6
    candidate_edges = [(u, v, d) for u, v, d in G.edges(data=True)
                       if d["tier"] in ("robust", "signif")]
    candidate_edges.sort(key=lambda e: e[2]["ratio"], reverse=True)
    PER_EDGE_LABEL_POS = {
        ("marital_status", "family_type"):  0.50,
        ("age_bin", "education_level"):     0.50,
        ("sex", "family_type"):              0.30,  # closer to sex
        ("age_bin", "marital_status"):      0.55,
        ("housing_type", "district"):       0.50,
        ("age_bin", "family_type"):         0.20,  # closer to age
    }
    def _key(u, v):
        return (u, v) if (u, v) in PER_EDGE_LABEL_POS else (v, u)
    for u, v, d in candidate_edges[:LABELED_TOP_N]:
        ratio = d["ratio"]
        text = f"×{ratio:.0f}" if ratio >= 10 else f"×{ratio:.1f}"
        pos = PER_EDGE_LABEL_POS.get(_key(u, v), 0.50)
        nx.draw_networkx_edge_labels(
            G, POS, edge_labels={(u, v): text}, font_size=11,
            label_pos=pos,
            bbox=dict(facecolor="white", edgecolor="#333", alpha=0.95, pad=2.5),
            ax=ax_net,
        )
    ax_net.set_axis_off()
    ax_net.set_title(
        f"(A) Robust + significant dependency edges  ({n_robust + n_signif} of 23)\n"
        "thickness ∝ log(ratio);   labeled = top-6 strongest edges  (×N = ratio over null bias floor)\n"
        "전체 23 edge 의 ratio 값은 (B) 차트에 모두 표시",
        fontsize=11, pad=12,
    )
    # add a touch of margin so node labels don't get clipped
    ax_net.margins(0.12)

    # --- (B) Right panel: ratio rank bar (all 23) ---
    sorted_edges = sorted(G.edges(data=True), key=lambda e: e[2]["ratio"], reverse=True)
    n_edges = len(sorted_edges)
    y = list(range(n_edges))[::-1]
    ratios = [d["ratio"] for _, _, d in sorted_edges]
    colors = [TIER[d["tier"]]["color"] for _, _, d in sorted_edges]
    labels = [f"{LABEL.get(u, u)} ~ {LABEL.get(v, v)}" for u, v, _ in sorted_edges]
    ax_bar.barh(y, ratios, color=colors, alpha=0.9, edgecolor="black", linewidth=0.4)
    ax_bar.axvline(2, color="#666", lw=0.8, ls="--", alpha=0.8)
    ax_bar.axvline(10, color="#666", lw=0.8, ls="--", alpha=0.8)
    ax_bar.set_xscale("log")
    ax_bar.set_xlabel("ratio = observed / null_p95   (log scale)", fontsize=10)
    ax_bar.set_yticks(y)
    ax_bar.set_yticklabels(labels, fontsize=9)
    ax_bar.set_xlim(0.7, 200)
    ax_bar.set_ylim(-0.7, n_edges - 0.3)  # tight, no top margin needed
    ax_bar.set_title("(B) All 23 edges ranked by bias-corrected ratio", fontsize=11, pad=12)
    ax_bar.tick_params(axis="x", labelsize=9)
    # ratio=2 / ratio=10 annotations placed inside the plot, at row 0 (just above bottom)
    ax_bar.annotate("ratio=2", xy=(2, -0.5), xytext=(2, -0.5),
                    ha="center", va="center", color="#666", fontsize=9,
                    bbox=dict(facecolor="white", edgecolor="none", pad=0.5, alpha=0.85))
    ax_bar.annotate("ratio=10", xy=(10, -0.5), xytext=(10, -0.5),
                    ha="center", va="center", color="#666", fontsize=9,
                    bbox=dict(facecolor="white", edgecolor="none", pad=0.5, alpha=0.85))
    ax_bar.grid(axis="x", alpha=0.2, which="both")

    # ===== legends below =====
    tier_handles = [
        plt.Line2D([0], [0], color=TIER["robust"]["color"], lw=5,
                   label=f"robust    (ratio ≥ 10)   {n_robust} edges"),
        plt.Line2D([0], [0], color=TIER["signif"]["color"], lw=3,
                   label=f"significant (2 ≤ ratio < 10)   {n_signif} edges"),
        plt.Line2D([0], [0], color=TIER["suspect"]["color"], lw=1.5, linestyle="--",
                   label=f"bias-suspect (ratio < 2)   {n_suspect} edges  "
                         "[in (B) only — omitted from network for clarity]"),
    ]
    grp_handles = [mpatches.Patch(color=GROUP_COLOR[g], label=g) for g in GROUP_COLOR]
    # Node group → 좌하 (panel A 의 노드에서만 사용)
    fig.legend(handles=grp_handles, loc="lower left", bbox_to_anchor=(0.04, -0.02),
               fontsize=10, title="Node group", title_fontsize=11, frameon=False, ncol=5)
    # Edge significance tier → 우하 (panel B 막대에 색으로 바로 적용)
    fig.legend(handles=tier_handles, loc="lower right", bbox_to_anchor=(0.96, -0.05),
               fontsize=10, title="Edge significance tier",
               title_fontsize=11, frameon=False, ncol=1)

    fig.suptitle(
        "Bias-corrected dependency skeleton  —  P4 permutation null applied",
        fontsize=13, y=1.00,
    )
    fig.savefig(OUT, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUT}")
    print(f"Tier counts: {counts}")


if __name__ == "__main__":
    main()
