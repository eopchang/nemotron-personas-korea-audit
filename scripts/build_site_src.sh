#!/usr/bin/env bash
# Prepare _site_src/ for MkDocs build.
#
# MkDocs forbids using the repo root as docs_dir. So we assemble a sibling
# directory _site_src/ that mirrors the repo structure for the .md files
# (and reports/figures images) that the site needs.
#
# Idempotent — safe to re-run.

set -euo pipefail

cd "$(dirname "$0")/.."  # repo root

SRC="_site_src"
rm -rf "$SRC"
mkdir -p "$SRC/docs" "$SRC/reports/tables" "$SRC/reports/figures" "$SRC/review"

# Root-level .md (README becomes index)
cp README.md         "$SRC/index.md"
cp ABSTRACT_EN.md    "$SRC/"
cp ROADMAP.md        "$SRC/"
cp CONTRIBUTING.md   "$SRC/"

# Guide docs
cp docs/*.md         "$SRC/docs/"

# Reports + tables
cp reports/*.md      "$SRC/reports/"
cp reports/tables/*.md "$SRC/reports/tables/"

# Figures (PNG, JPG, SVG) — keep subdirectory structure
rsync -a --include='*/' --include='*.png' --include='*.jpg' --include='*.svg' \
      --exclude='*' reports/figures/ "$SRC/reports/figures/"

# Review docs (skip the huge auto-generated REVIEW_PACKET.md — it's for LLM
# review packet, not human site reading)
cp review/README.md             "$SRC/review/"
cp review/CLAIMS_LEDGER.md      "$SRC/review/"
cp review/REVIEW_PROMPTS.md     "$SRC/review/"
cp review/REVIEW_PROMPTS_EN.md  "$SRC/review/"

echo "  built $SRC/ from $(find "$SRC" -name '*.md' | wc -l | tr -d ' ') markdown files"
