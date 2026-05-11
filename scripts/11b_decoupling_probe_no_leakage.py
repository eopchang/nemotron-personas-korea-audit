"""Leakage-corrected re-run of the decoupling probe.

Critical examination identified two potential leakage sources in 11_decoupling_probe.py:

  L1. OrdinalEncoder.fit_transform was called on the FULL data including future
      test rows — encoder learned the universe of categorical values from test too.
  L2. cap_high_card (occupation top-249 + '기타') was computed on the FULL data —
      the choice of which categories survive depended on test-set frequencies too.

Both are mild for this kind of analysis (encoder doesn't use Y, top-K by frequency
is structurally stable in 80/20 splits), but to be rigorous we re-run with strict
isolation: fit encoders, compute the cap, AND apply 5-fold CV — all train-only.

If headline conclusions (housing decoupling = info_added ≈ 0) remain after this
correction, leakage was NOT a meaningful threat to validity.

Outputs:
  data/processed/decoupling_probe_no_leakage.json     — same structure as original
  Console: side-by-side comparison of corrected vs original info_added
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import log_loss
from sklearn.model_selection import KFold
from sklearn.preprocessing import OrdinalEncoder

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import ROOT, load_df

OUT = ROOT / "data" / "processed" / "decoupling_probe_no_leakage.json"
ORIG = ROOT / "data" / "processed" / "decoupling_probe.json"
SEED = 42
N_SUB = 300_000
CARD_CAP = 250
N_FOLDS = 5


def cap_train_only(train_df, test_df, cols):
    """Compute top-K from TRAIN only; apply same mapping to test (rest -> '기타')."""
    train_out = train_df[cols].copy()
    test_out = test_df[cols].copy()
    for col in cols:
        n_unique = train_out[col].nunique()
        if n_unique > CARD_CAP:
            top = train_out[col].value_counts().head(CARD_CAP - 1).index
            mask = train_out[col].isin(top)
            train_out[col] = train_out[col].where(mask, "기타")
            mask_t = test_out[col].isin(top)
            test_out[col] = test_out[col].where(mask_t, "기타")
    return train_out, test_out


def fit_eval_one_fold(train_pd, test_pd, target, features, n_classes_global) -> dict:
    """Train-only encoding + cap. Returns CE on test fold."""
    Xtr_raw, Xte_raw = cap_train_only(train_pd, test_pd, features)
    ytr_raw, yte_raw = cap_train_only(train_pd, test_pd, [target])

    enc_X = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    Xtr = enc_X.fit_transform(Xtr_raw)
    Xte = enc_X.transform(Xte_raw)

    enc_y = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    ytr = enc_y.fit_transform(ytr_raw).ravel().astype(int)
    yte_raw_arr = enc_y.transform(yte_raw).ravel().astype(int)

    # Test rows whose target wasn't seen in training: drop (can't score)
    keep = yte_raw_arr >= 0
    Xte = Xte[keep]
    yte = yte_raw_arr[keep]

    n_classes_train = int(ytr.max() + 1)

    clf = HistGradientBoostingClassifier(
        max_iter=200, max_depth=8, learning_rate=0.05,
        categorical_features=list(range(Xtr.shape[1])),
        random_state=SEED,
    )
    clf.fit(Xtr, ytr)
    p = clf.predict_proba(Xte)
    if p.shape[1] < n_classes_train:
        full = np.zeros((p.shape[0], n_classes_train))
        full[:, clf.classes_.astype(int)] = p
        p = full
    ce = float(log_loss(yte, p, labels=np.arange(n_classes_train)))
    acc = float((p.argmax(axis=1) == yte).mean())
    return {"CE": ce, "acc": acc, "n_test": int(len(yte)),
            "n_classes_train": n_classes_train,
            "n_dropped_unseen_target": int((~keep).sum())}


def run_kfold(sub_pd, target, features, n_folds: int) -> dict:
    """Run K-fold CV with train-only encoding."""
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=SEED)
    fold_results = []
    n_classes_global = sub_pd[target].nunique()
    for fold_idx, (tr_idx, te_idx) in enumerate(kf.split(sub_pd)):
        tr = sub_pd.iloc[tr_idx]
        te = sub_pd.iloc[te_idx]
        r = fit_eval_one_fold(tr, te, target, features, n_classes_global)
        fold_results.append(r)
    ces = [r["CE"] for r in fold_results]
    accs = [r["acc"] for r in fold_results]
    return {
        "mean_CE": float(np.mean(ces)),
        "std_CE": float(np.std(ces, ddof=1)),
        "mean_acc": float(np.mean(accs)),
        "n_folds": n_folds,
        "fold_CEs": ces,
    }


def main() -> None:
    print(f"Loading & subsampling to {N_SUB:,}...", flush=True)
    df = load_df()
    sub = df.sample(n=N_SUB, seed=SEED, with_replacement=False).to_pandas()
    print(f"  loaded {len(sub):,} rows", flush=True)

    # Same cases as original
    cases = [
        ("housing_type", ["district"], ["district", "age_bin", "sex",
                                         "marital_status", "family_type",
                                         "education_level", "bachelors_field",
                                         "occupation"], "Q1 housing decoupled?"),
        ("family_type", ["district"], ["district", "age_bin", "sex",
                                        "marital_status", "education_level"],
         "Control: family_type"),
        ("occupation", ["district", "province"], ["district", "province",
                                                    "age_bin", "sex",
                                                    "education_level",
                                                    "bachelors_field"],
         "Control: occupation"),
        ("military_status", ["age_bin"], ["age_bin", "sex"], "Q2 military|age+sex"),
        ("military_status", ["sex"], ["sex", "age_bin", "occupation"],
         "Q3 military|sex+age+occupation"),
        ("marital_status", ["age_bin"], ["age_bin", "sex", "education_level",
                                          "family_type"],
         "Control: marital"),
    ]

    out = []
    for target, base, full, q in cases:
        print(f"\n=== {q}", flush=True)
        print(f"   target={target}", flush=True)
        t0 = time.time()
        b = run_kfold(sub, target, base, N_FOLDS)
        print(f"   baseline (5-fold CV, train-only enc):  "
              f"CE={b['mean_CE']:.4f} ± {b['std_CE']:.4f}  acc={b['mean_acc']:.3f}  "
              f"({(time.time()-t0):.1f}s)", flush=True)
        t0 = time.time()
        f = run_kfold(sub, target, full, N_FOLDS)
        print(f"   full     (5-fold CV, train-only enc):  "
              f"CE={f['mean_CE']:.4f} ± {f['std_CE']:.4f}  acc={f['mean_acc']:.3f}  "
              f"({(time.time()-t0):.1f}s)", flush=True)

        n_pop = sub[target].value_counts(normalize=True).values
        ce_null = float(-(n_pop * np.log(n_pop)).sum())
        info_baseline = ce_null - b["mean_CE"]
        info_added = b["mean_CE"] - f["mean_CE"]
        info_total = ce_null - f["mean_CE"]

        out.append({
            "question": q, "target": target,
            "baseline_features": base, "full_features": full,
            "CE_null": ce_null,
            "CE_baseline_mean": b["mean_CE"], "CE_baseline_std": b["std_CE"],
            "CE_full_mean": f["mean_CE"],     "CE_full_std": f["std_CE"],
            "acc_baseline_mean": b["mean_acc"], "acc_full_mean": f["mean_acc"],
            "info_in_baseline": info_baseline,
            "info_added_by_extras": info_added,
            "info_total": info_total,
            "fraction_added": info_added / info_total if info_total > 1e-9 else 0,
            "n_folds": N_FOLDS,
        })
        print(f"   info_added (corrected) = {info_added:+.4f} nats  "
              f"share = {(info_added/info_total*100 if info_total>1e-9 else 0):+.1f}%", flush=True)

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"\nWrote {OUT}", flush=True)

    # Side-by-side comparison with original
    if ORIG.exists():
        orig = json.loads(ORIG.read_text())
        print("\n" + "=" * 78)
        print("COMPARISON: original (single split, full-data encoder) vs leakage-corrected (5-fold CV, train-only)")
        print("=" * 78)
        print(f"{'Question':45s}  {'orig info_added':>18s}  {'corr info_added':>18s}  diff")
        for o, c in zip(orig, out):
            d = c["info_added_by_extras"] - o["info_added_by_extras"]
            print(f"{o['question'][:45]:45s}  {o['info_added_by_extras']:+18.5f}  "
                  f"{c['info_added_by_extras']:+18.5f}  {d:+.5f}")


if __name__ == "__main__":
    main()
