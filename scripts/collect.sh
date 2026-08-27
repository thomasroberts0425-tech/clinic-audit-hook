#!/usr/bin/env bash
# Collect ICP signals for one clinic URL.
#
#   scripts/collect.sh <clinic-url> [outdir]
#
# One Firecrawl call (markdown + rawHtml + links + metadata), then a pure-stdlib
# extractor. No LLM in this path -- the output is the same every run, which is
# what makes the skill's judgment auditable.
set -euo pipefail

URL="${1:?usage: collect.sh <clinic-url> [outdir]}"
OUT="${2:-.audit}"
SLUG=$(printf '%s' "$URL" | sed -E 's#https?://##; s#^www\.##; s#[/?].*##; s#[^a-zA-Z0-9.-]#_#g')

mkdir -p "$OUT"
RAW="$OUT/$SLUG.raw.json"
SIG="$OUT/$SLUG.signals.json"

if ! command -v firecrawl >/dev/null 2>&1; then
  echo "error: firecrawl CLI not found. Install it, or set FIRECRAWL_API_KEY and use npx firecrawl." >&2
  exit 127
fi

# --wait-for lets JS-injected booking widgets land before we read the DOM.
firecrawl scrape "$URL" \
  --format markdown,links,rawHtml \
  --wait-for 2500 \
  -o "$RAW" >/dev/null

python3 "$(dirname "$0")/extract_signals.py" "$RAW" "$URL" | tee "$SIG"
