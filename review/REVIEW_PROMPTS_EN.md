# External-Model Review Prompts (English)

Copy-paste-ready prompts for GPT / Claude / Gemini long-context models.

**Usage**: First attach (or paste) [`REVIEW_PACKET.md`](REVIEW_PACKET.md) to the model. Then paste one of the prompts below.

*(The Korean original is at [`REVIEW_PROMPTS.md`](REVIEW_PROMPTS.md). Detailed context: [`../ABSTRACT_EN.md`](../ABSTRACT_EN.md).)*

> **Note on the packet**: REVIEW_PACKET.md is in Korean (it bundles the full Korean reports for self-contained review). Most modern long-context models handle Korean+English mixed prompts well — feel free to instruct the model in English even though the source material is Korean. The structured numerical artifact [`key_results.json`](key_results.json) is language-neutral (English keys).

---

## 🎯 Prompt 0a — Falsification mode (most aggressive critique)

```text
You are a senior statistician with deep expertise in synthetic-data evaluation.
Your task is to ATTEMPT TO REFUTE the conclusions in the attached REVIEW_PACKET.
This is not a friendly review — it is adversarial critique.

The packet is in Korean but contains numbered claims and structured tables; the
key numerical results are also mirrored in English-keyed JSON
(key_results.json, included in the packet).

Respond in this format:

[1] For each of the report's 6 headline findings (province/district fidelity;
    demographic chain; gender × major separation; housing decoupling;
    military-as-occupation-function; occupation "no-occupation" category) plus
    the self-stated high-cardinality-bias caveat — describe what analytical
    result would have to appear to falsify that conclusion. Propose 1–2
    concrete falsification tests per finding.

[2] Find at least 5 statements in the report whose strength of language
    exceeds the evidence level. Quote them verbatim and propose a safer
    rewording.

[3] Identify at least 3 claims in CLAIMS_LEDGER (36 claims, ★ rated) whose
    confidence rating you believe is overstated. Give the downgrade reason.

[4] Pick the single conclusion in this report that an outside expert would
    find hardest to trust. Describe in detail what additional analysis would
    be required to make it trustworthy.

You may behave like an NVIDIA-side lawyer — i.e., if this audit unfairly
disparages the dataset anywhere, point that out too.
```

---

## 🎯 Prompt 0 — Integrated review (most commonly used)

```text
You are a senior researcher fluent in statistics, information theory, and
synthetic-data evaluation. The attached REVIEW_PACKET is an independent audit
of NVIDIA's Nemotron-Personas-Korea, a 1M-row synthetic persona dataset for
Korea.

Evaluate the audit objectively along the four axes below and conclude with
an overall judgment.

[1. Methodological soundness]
- Is the Conditional Mutual Information (CMI) computation consistent with
  the standard definition?
- How much does the PC-style skeleton recovery's |Z| ≤ 2 limit weaken the
  conclusions?
- Does the within-synthetic predictability check (HGB classifier, 300K
  subsample, info_added metric) measure what it claims to measure?
- Are there standard validation tools that the audit skipped (e.g., pMSE,
  discriminator AUC, propensity-score differences)?

[2. Statistical justification]
- Are the effect-size thresholds (TVD < 0.05, ε = 0.005 nats) appropriate?
- Is the decision to ignore χ² at N=1M and use only effect sizes defensible?
- Can info_added = −0.008 nats really be interpreted as "0" given the
  single-model limitation and sample variability?
- Is the stability check (5 seeds × 200K) sufficient?

[3. Domain interpretation (Korean demographics)]
- Are KOSIS / Statistics Korea reference numbers cited correctly?
- Do Korean demographic interpretations (widow rate, cohort education,
  military service age) match Korean reality?
- Is the "housing decoupling" finding justified relative to Korean housing
  market reality?
- Is the "military as occupation function" interpretation reasonable or
  overstated?

[4. Reproducibility & transparency]
- For each of CLAIMS_LEDGER's 36 claims: is the evidence clearly tied or
  ambiguous?
- Are code → output mappings explicit?
- Are arbitrary choices (thresholds, seeds, sample sizes) sufficiently
  declared?

[Final judgment]
Conclude with:
- Classify the audit's 6 headline findings into high / medium / low
  confidence.
- Top 3 weaknesses.
- Top 3 additional verifications that would strengthen the audit.
- A one-line verdict on whether this audit is citation-worthy.
```

---

## 🔬 Prompt 1 — Methodology deep-dive

```text
You are a senior statistician with deep expertise in Probabilistic Graphical
Models, information theory, and causal inference. Focus your review on Phase
3 (PGM structure inference) of the attached REVIEW_PACKET.

Address:

1. CMI definition & implementation
   - Is I(X;Y|Z) computed in nats consistent with the standard definition?
   - Do the limitations of plug-in estimation on 3D contingency tables
     (sparse cells, plug-in bias) materially affect the results?
   - Beyond the plug-in MLE used here, are there better alternatives
     (MIXED, kNN-based) that should be tried?

2. PC-style skeleton recovery
   - How does this implementation differ from the standard PC algorithm
     (|Z| ≤ 2 cap, single-Z first, etc.)?
   - Is the "best mediator + 1 more" heuristic more conservative or more
     aggressive than orthodox PC's power-set conditioning?
   - Suggest candidate edges that may have been wrongly included or wrongly
     excluded from the inferred skeleton.

3. Within-synthetic predictability check (originally "decoupling probe")
   - Does HistGradientBoostingClassifier capture categorical dependence
     well, or might it miss subtle dependencies?
   - Is the procedure of interpreting log-loss differences in nats correct?
   - Comment on the single-seed (42) reliance and the absence of stratified
     splitting.
   - What is the statistical meaning of "info_added < 0"?

4. Which of these would most likely change the conclusions:
   - Extending |Z| to 3 or the full power set
   - Using a regularized estimator
   - Block-bootstrap CIs for CMI
   - A different structure-learning algorithm (NOTEARS, GES, GraNDAG)

Length: 1500–2500 words.
Format: for each of the four sections — (a) assessment, (b) specific
concerns, (c) recommendation.
```

---

## 📊 Prompt 2 — Statistical-justification deep-dive

```text
You are a data scientist with strong expertise in effect-size statistics
and large-sample interpretation. Evaluate every threshold and arbitrary
choice in the attached REVIEW_PACKET.

Targets (see METHODOLOGY §10 table):
1. age binning [19-24, 25-34, …, 85+]
2. TVD "good fidelity" threshold < 0.05
3. CMI effect-size threshold ε = 0.005 nats
4. PC conditioning depth |Z| ≤ 2
5. Within-synthetic predictability check subsample size 300,000
6. HGB 200 iter / depth 8 / lr 0.05
7. HGB cardinality cap 250
8. Stability 200,000 × 5 seeds

For each:
- How much does this choice strengthen or weaken the report's conclusions?
- What more conservative / more aggressive alternative threshold would be
  reasonable?
- If a sensitivity analysis were performed, what would you expect to
  happen?

Specifically address:
A. If CMI threshold ε were changed to 0.001 or 0.01, how many of the 23
   direct edges would re-classify, and in which direction?
B. How trustworthy is info_added = −0.008 nats relative to sampling
   variation? What standard error would 5-seed × HGB give roughly?
C. Justify (or contest) the decision to ignore χ² p-values at N=1M.

Conclude with the top 3 statistical robustness checks the audit should
strengthen, in priority order.
```

---

## 🇰🇷 Prompt 3 — Korean domain validation

```text
You are a domain expert in Korean demographics, labor, and housing — or
have PhD-level knowledge in Korean social science. Verify the Korean-reality
interpretations in the attached REVIEW_PACKET.

Check:

1. KOSIS / Statistics Korea reference accuracy
   - Do the six reference distributions in data/reference/kosis_reference.json
     (included in REVIEW_PACKET) match the actual KOSIS / Statistics Korea
     published numbers?
   - Are caveats about population-frame differences (15+, 19+, 25+,
     household, individual) handled appropriately?
   - Are there more suitable references (different years, different
     statistics) that should have been used?

2. Justification of Korean demographic-pattern interpretations
   - Do 19–24 unmarried 95.4%, 25–34 unmarried 65.3% match Korea's
     delayed-marriage / non-marriage trend?
   - Do 75–84 widowed 42.6%, 85+ widowed 70.7% match life-expectancy
     differences?
   - Do 25–34 4-year-college 51.6%, 85+ no-schooling 37.4% match Korean
     cohort education change?
   - Does the "65+ not-employed" pattern match Korean retirement / pension
     systems?

3. Domain validity of the core concerns
   - Does the active-duty rank breakdown (privates 25 / NCOs 41 / officers
     47, women 11%) match Korean military's actual composition? See
     data/processed/military_breakdown.json.
   - "Living alone" ~14% (per-person) vs. Statistics Korea 2023 single-person
     households 35% (per-household) — did the audit clearly flag this
     unit-difference as preventing direct comparison?
   - Do "engineering 86% male, health 28% male" precisely match Korean
     4-year-college graduate sex-ratio statistics?
   - Is "housing decoupling" a justified concern relative to Korean housing
     market reality (single-person officetels, youth rentals)?

4. Korea-specific analyses the audit missed
   - What Korean patterns should have been checked but weren't?
   - Could rural-vs-urban or capital-vs-non-capital coarse splits have
     enriched the analysis?
   - Origin / migration patterns, foreigners / multicultural households —
     aspects the dataset does not cover.

Conclude with:
- Top 3 most trustworthy Korean-domain interpretations
- Top 3 most suspect ones
- What a Korean social scientist should additionally verify before using
  the dataset
```

---

## 🔧 Prompt 4 — Reproducibility & code review

```text
You are a reproducibility-assessment expert. Audit the code / data / output
mappings in the attached REVIEW_PACKET.

Evaluate:

1. CLAIMS_LEDGER's 36 claims → evidence-file mapping
   - For each claim, can the cited CSV/JSON/figure be directly used to
     verify it?
   - Which claims have unclear or weak evidence mapping?

2. Disclosure of arbitrary choices
   - Are all random seeds declared?
   - Are thresholds, sample sizes, and preprocessing decisions explicit in
     code AND summarized in METHODOLOGY?

3. Environment / dependencies
   - Is requirements.txt sufficient (with version pins)?
   - Any sources of non-determinism (HGB multi-threading, scikit-learn
     version drift)?

4. Code → output → report consistency
   - Do per-phase numbers in the report exactly match the code outputs?
     (Use key_results.json in REVIEW_PACKET.)
   - Are tables and figures in the report verifiably built from the
     declared output files?

5. Third-party reproducibility
   - Can a fresh user reproduce all results from README alone?
   - Missing documentation or environment-setup steps?
   - External dependencies beyond the HuggingFace data download?

For each issue found:
- Issue: what is missing or wrong
- Impact: which conclusions are affected
- Recommendation: how to fix

Conclude with a "reproducibility score" (1–10) and rationale.
```

---

## 💡 Tips

- Prefer **long-context models** over RAG (the PACKET should be read in one shot for coherent evaluation).
- If the model questions KOSIS numbers, enabling web search / browsing helps it verify against the actual KOSIS site.
- Please share results as a GitHub issue using the [`.github/ISSUE_TEMPLATE/external_review.md`](../.github/ISSUE_TEMPLATE/external_review.md) template (label `external-review`).
- Mixed-language responses are fine — feel free to respond in either English or Korean as suits you.
