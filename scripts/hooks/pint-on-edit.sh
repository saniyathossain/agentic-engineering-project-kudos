#!/bin/bash
# PostToolUse hook: format edited PHP files with Pint inside the app container (best effort).
f=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))')
case "$f" in
  */codes/*.php)
    rel="${f#*/codes/}"
    root="$(cd "$(dirname "$0")/../.." && pwd)"
    docker compose -f "$root/docker/docker-compose.yml" exec -T app vendor/bin/pint "$rel" >/dev/null 2>&1 || true ;;
esac
exit 0
