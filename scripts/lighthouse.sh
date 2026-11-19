#!/bin/sh
# Lighthouse (the engine behind Google PageSpeed Insights) against the production-style stack.
#   scripts/lighthouse.sh <path> <name> [mobile|desktop] [light|dark]
# Runs inside the prod compose network (project kudos-prod), so it needs `make prod`-style containers up
# (docker compose -p kudos-prod ... up -d). Writes docs/performance/<name>-<form>-<scheme>.report.{html,json}.
set -eu
cd "$(dirname "$0")/.."
PATH_ARG="${1:-/}"; NAME="${2:-page}"; FORM="${3:-mobile}"; SCHEME="${4:-light}"
NETWORK="${LIGHTHOUSE_NETWORK:-kudos-prod_edge}"
TARGET="${LIGHTHOUSE_TARGET:-http://web:8080}"
SCHEME_FLAG=""; [ "$SCHEME" = "dark" ] && SCHEME_FLAG="--blink-settings=preferredColorScheme=1"
PRESET=""; [ "$FORM" = "desktop" ] && PRESET="--preset=desktop"

docker run --rm --network "$NETWORK" --security-opt seccomp=unconfined \
  -v "$PWD/docs/performance:/out" --entrypoint sh zenika/alpine-chrome:with-node -c "
    npx --yes lighthouse@latest '$TARGET$PATH_ARG' $PRESET \
      --chrome-path=/usr/bin/chromium-browser \
      --chrome-flags='--headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage $SCHEME_FLAG' \
      --only-categories=performance,accessibility,best-practices,seo \
      --output=json --output=html --output-path=/out/$NAME-$FORM-$SCHEME --quiet
  "
python3 - "docs/performance/$NAME-$FORM-$SCHEME.report.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
c, a = d['categories'], d['audits']
scores = {k: round(v['score'] * 100) for k, v in c.items()}
print(scores, 'LCP', a['largest-contentful-paint']['displayValue'], 'CLS', a['cumulative-layout-shift']['displayValue'], 'TBT', a['total-blocking-time']['displayValue'])
PY
