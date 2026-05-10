"""Network diagram of recovered PGM-implied skeleton.

Two figures:
  reports/figures/skeleton_network.png   — direct edges only, edge thickness = surviving CMI
  reports/figures/skeleton_compare.png   — side-by-side: marginal MI graph vs skeleton

Layout uses a manually fixed pos dict so the structure is readable across runs.

Color encoding for edges:
  - dark blue: direct (mediated_max < 0.3)
  - blue:     direct but partly mediated (0.3 <= med_max < 0.7)
  - light gray, dashed: mediated edges (shown only on the comparison panel)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import ROOT, setup_korean_font

OUT_DIR = ROOT / "data" / "processed" / "cmi"
FIG_DIR = ROOT / "reports" / "figures"
setup_korean_font()

# Manual layout reflecting domain structure (top = exogenous, bottom = derived)
POS = {
    "age_bin":         (-0.7, 1.0),
    "sex":             ( 0.7, 1.0),
    "province":        (-2.4, 0.0),
    "district":        (-2.4,-0.5),
    "housing_type":    (-2.4,-1.4),
    "education_level": (-1.0, 0.0),
    "bachelors_field": (-0.4,-0.6),
    "marital_status":  ( 0.6, 0.0),
    "family_type":     ( 1.4,-0.6),
    "occupation":      ( 0.0,-1.4),
    "military_status": ( 1.4,-1.4),
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


def edge_color(rec: dict) -> str:
    drop = rec["drop_max_any"]
    if drop < 0.3:
        return "#1f3a93"
    return "#5e8bcf"


def edge_width(mi: float) -> float:
    # log-scale; keep within readable range
    import math
    return max(0.6, min(6.5, 0.7 + 1.6 * math.log1p(20 * mi)))


def main() -> None:
    skel = pd.read_csv(OUT_DIR / "skeleton.csv")
    direct = skel[skel.edge_class == "direct"]
    mediated = skel[skel.edge_class == "mediated"]

    G = nx.Graph()
    for n in POS.keys():
        G.add_node(n)
    for r in direct.itertuples():
        G.add_edge(r.x, r.y, mi=r.mi_xy, cmi=r.cmi_min_any,
                   drop=r.drop_max_any, mediator=r.z_star_pair)

    # ---------- Figure 1: skeleton only ----------
    fig, ax = plt.subplots(figsize=(13, 9))
    node_colors = [GROUP_COLOR[NODE_GROUP[n]] for n in G.nodes]
    nx.draw_networkx_nodes(G, POS, node_size=2400, node_color=node_colors,
                           edgecolors="black", linewidths=1.2, ax=ax)
    nx.draw_networkx_labels(G, POS, font_size=9, font_family=plt.rcParams["font.family"], ax=ax)
    for u, v, d in G.edges(data=True):
        nx.draw_networkx_edges(G, POS, edgelist=[(u, v)],
                               width=edge_width(d["mi"]),
                               edge_color=edge_color({"drop_max_any": d["drop"]}),
                               alpha=0.85, ax=ax)
    edge_labels = {(u, v): f"{d['mi']:.2f}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, POS, edge_labels=edge_labels, font_size=7,
                                 bbox=dict(facecolor="white", edgecolor="none", alpha=0.6),
                                 ax=ax)
    ax.set_title(f"Recovered skeleton — {len(G.edges)} direct edges (PC-style, |Z|≤2)\n"
                 "edge label = marginal MI (nats); thickness = MI; "
                 "dark blue = direct (drop<30%), blue = partly mediated", fontsize=11)
    ax.set_axis_off()
    legend_handles = [plt.Line2D([0], [0], marker="o", linestyle="",
                                 markerfacecolor=c, markeredgecolor="black",
                                 markersize=11, label=g)
                      for g, c in GROUP_COLOR.items()]
    ax.legend(handles=legend_handles, loc="lower left", fontsize=9, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "skeleton_network.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    # ---------- Figure 2: marginal vs skeleton ----------
    fig, axes = plt.subplots(1, 2, figsize=(20, 9))

    # left: all marginal edges with mi >= 0.005
    Gm = nx.Graph()
    for n in POS.keys():
        Gm.add_node(n)
    for r in skel.itertuples():
        if r.mi_xy >= 0.005:
            Gm.add_edge(r.x, r.y, mi=r.mi_xy, drop=r.drop_max_any,
                        klass=r.edge_class)
    ax = axes[0]
    nx.draw_networkx_nodes(Gm, POS, node_size=1900,
                           node_color=[GROUP_COLOR[NODE_GROUP[n]] for n in Gm.nodes],
                           edgecolors="black", linewidths=1.0, ax=ax)
    nx.draw_networkx_labels(Gm, POS, font_size=8,
                            font_family=plt.rcParams["font.family"], ax=ax)
    for u, v, d in Gm.edges(data=True):
        if d["klass"] == "direct":
            color = "#1f3a93"; style = "solid"; alpha = 0.95
        else:
            color = "#999999"; style = "dashed"; alpha = 0.7
        nx.draw_networkx_edges(Gm, POS, edgelist=[(u, v)],
                               width=edge_width(d["mi"]),
                               edge_color=color, style=style, alpha=alpha, ax=ax)
    ax.set_title(f"All marginal-dependent pairs (|MI|≥0.005)\n"
                 f"solid blue = direct after PC ({len(direct)})  ·  "
                 f"dashed gray = mediated ({len(mediated)})", fontsize=11)
    ax.set_axis_off()

    # right: skeleton only
    ax = axes[1]
    nx.draw_networkx_nodes(G, POS, node_size=1900,
                           node_color=[GROUP_COLOR[NODE_GROUP[n]] for n in G.nodes],
                           edgecolors="black", linewidths=1.0, ax=ax)
    nx.draw_networkx_labels(G, POS, font_size=8,
                            font_family=plt.rcParams["font.family"], ax=ax)
    for u, v, d in G.edges(data=True):
        nx.draw_networkx_edges(G, POS, edgelist=[(u, v)],
                               width=edge_width(d["mi"]),
                               edge_color=edge_color({"drop_max_any": d["drop"]}),
                               alpha=0.9, ax=ax)
    ax.set_title(f"Recovered skeleton (direct only, {len(G.edges)} edges)", fontsize=11)
    ax.set_axis_off()

    fig.suptitle("PGM 구조 추론: 마지널 의존 → 직접 edge 골라내기 (PC-style, ε=0.005 nats)",
                 fontsize=13, y=0.995)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "skeleton_compare.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    # ---------- node degree summary ----------
    deg = sorted(G.degree, key=lambda kv: -kv[1])
    print("Node degrees in recovered skeleton:")
    for n, d in deg:
        print(f"  {n:18s}  {d}")
    summ = pd.DataFrame(deg, columns=["node", "degree"])
    summ.to_csv(OUT_DIR / "node_degrees.csv", index=False)
    print(f"\nWrote {FIG_DIR}/skeleton_network.png")
    print(f"Wrote {FIG_DIR}/skeleton_compare.png")


if __name__ == "__main__":
    main()
