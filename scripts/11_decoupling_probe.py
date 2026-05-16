"""Within-synthetic predictability check (합성-내 예측가능성 검사).

This is a within-synthetic probe: we train/test split the synthetic data and
compare cross-entropy with vs without an extra feature set. It is NOT TSTR
(Train on Synthetic, Test on REAL) since we never evaluate on real data.

(File name retains the legacy `decoupling_probe` identifier for external
reference stability — see docs/GLOSSARY.md for the canonical term.)

For each (target, baseline-features, full-features) triple:
  - train HistGradientBoostingClassifier on baseline
  - train another on full
  - compare cross-entropy + accuracy on a held-out 20% test split
  - large improvement (full vs baseline) ⇒ extra features add information
  - tiny improvement ⇒ extra features are conditionally independent of target
                        given baseline (i.e., decoupled in PGM)

We stratify the comparison by 6 target-feature triples to triangulate which
parts of the PGM are richly tied vs decoupled.

Subsample N=300,000 for tractable training (HGB on 1M with high-card cats is
slow; signal-to-noise at 300K is more than adequate for our metric scale).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import log_loss
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import ROOT, load_df

OUT = ROOT / "data" / "processed" / "decoupling_probe.json"
SEED = 42
N_SUB = 300_000


CARD_CAP = 250  # HGB caps categorical features at 255; cap to top-K + '기타'


def cap_high_card(df_pd, features: list[str]) -> "pandas.DataFrame":
    out = df_pd[features].copy()
    for col in features:
        n_unique = out[col].nunique()
        if n_unique > CARD_CAP:
            top = out[col].value_counts().head(CARD_CAP - 1).index
            out[col] = out[col].where(out[col].isin(top), "기타")
    return out


def fit_eval(df_pd, target: str, features: list[str]) -> dict:
    Xframe = cap_high_card(df_pd, features)
    yframe = cap_high_card(df_pd, [target])
    enc = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    X = enc.fit_transform(Xframe)
    y_enc = OrdinalEncoder().fit_transform(yframe).ravel().astype(int)
    n_classes = len(np.unique(y_enc))

    Xtr, Xte, ytr, yte = train_test_split(
        X, y_enc, test_size=0.2, random_state=SEED, stratify=None
    )
    # Treat all features as categorical
    clf = HistGradientBoostingClassifier(
        max_iter=200, max_depth=8, learning_rate=0.05,
        categorical_features=list(range(X.shape[1])),
        random_state=SEED,
    )
    clf.fit(Xtr, ytr)
    p = clf.predict_proba(Xte)
    if p.shape[1] < n_classes:
        # pad missing classes with zero prob (shouldn't happen with stratify)
        full = np.zeros((p.shape[0], n_classes))
        full[:, clf.classes_.astype(int)] = p
        p = full
    ce = float(log_loss(yte, p, labels=np.arange(n_classes)))
    acc = float((p.argmax(axis=1) == yte).mean())
    return {"CE": ce, "acc": acc, "n_test": int(len(yte)), "n_classes": int(n_classes)}


def main() -> None:
    df = load_df()
    print(f"loading & subsampling to {N_SUB:,}...")
    sub = df.sample(n=N_SUB, seed=SEED, with_replacement=False).to_pandas()

    cases = [
        # target, baseline_features, full_features, hypothesis
        ("housing_type", ["district"], ["district", "age_bin", "sex",
                                         "marital_status", "family_type",
                                         "education_level", "bachelors_field",
                                         "occupation"],
         "Q1 housing decoupled from person attrs given district?"),
        ("family_type", ["district"], ["district", "age_bin", "sex",
                                        "marital_status", "education_level"],
         "Control: family_type SHOULD improve with marital/age (tested edge)"),
        ("occupation", ["district", "province"], ["district", "province",
                                                    "age_bin", "sex",
                                                    "education_level",
                                                    "bachelors_field"],
         "Control: occupation IS modeled with sex/edu/field"),
        ("military_status", ["age_bin"], ["age_bin", "sex"],
         "Q2 military depends on sex but does it on age?"),
        ("military_status", ["sex"], ["sex", "age_bin", "occupation"],
         "Q3 if we add occupation, military becomes determined?"),
        ("marital_status", ["age_bin"], ["age_bin", "sex", "education_level",
                                          "family_type"],
         "Control: marital should improve with family_type (direct edge)"),
    ]

    out = []
    for target, base, full, q in cases:
        print(f"\n=== {q}")
        print(f"   target = {target}")
        print(f"   baseline = {base}")
        b = fit_eval(sub, target, base)
        print(f"   baseline:  CE={b['CE']:.4f}, acc={b['acc']:.3f}")
        f = fit_eval(sub, target, full)
        print(f"   full    :  CE={f['CE']:.4f}, acc={f['acc']:.3f}")
        # 'null' = predict marginal of target
        n_pop = sub[target].value_counts(normalize=True).values
        ce_null = float(-(n_pop * np.log(n_pop)).sum())
        info_baseline = ce_null - b["CE"]
        info_added = b["CE"] - f["CE"]
        info_total = ce_null - f["CE"]
        out.append({
            "question": q,
            "target": target,
            "baseline_features": base,
            "full_features": full,
            "CE_null": ce_null,
            "CE_baseline": b["CE"],
            "CE_full": f["CE"],
            "acc_baseline": b["acc"],
            "acc_full": f["acc"],
            "info_in_baseline": info_baseline,
            "info_added_by_extras": info_added,
            "info_total": info_total,
            "fraction_added": info_added / info_total if info_total > 1e-9 else 0,
        })
        print(f"   info(null→base) = {info_baseline:.4f}  "
              f"info(base→full) = {info_added:.4f}  "
              f"added share = {(info_added/info_total*100 if info_total>1e-9 else 0):.1f}%")

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
