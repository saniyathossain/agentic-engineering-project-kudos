#!/bin/sh
# Records the product tour against the production-style stack (http://localhost:8011) and writes docs/demo/kudos-tour.mp4 at 30 fps.
set -eu
cd "$(dirname "$0")/../.."
OUT="$PWD/docs/demo"
mkdir -p "$OUT" .tmp-demo
rm -f .tmp-demo/*.webm
docker run --rm --ipc=host --add-host host.docker.internal:host-gateway \
  -v "$PWD/scripts/demo:/demo:ro" -v "$PWD/.tmp-demo:/out" -w /work \
  mcr.microsoft.com/playwright:v1.65.1-noble sh -c "mkdir -p /work && cd /work && npm init -y >/dev/null && npm i --silent playwright-core@1.65.1 && cp /demo/tour.mjs . && node tour.mjs"
ffmpeg -y -loglevel error -i .tmp-demo/*.webm -vf "fps=30,scale=1280:-2:flags=lanczos" -c:v libx264 -preset slow -crf 24 -pix_fmt yuv420p -movflags +faststart "$OUT/kudos-tour.mp4"
rm -rf .tmp-demo
echo "Wrote $OUT/kudos-tour.mp4"
