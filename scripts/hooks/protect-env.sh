#!/bin/bash
# PreToolUse hook: block Claude from editing secret env files.
f=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))')
case "$f" in
  */docker/.envs/app.env|*/codes/.env|*/.env)
    echo "Blocked: $f holds local secrets. Edit app.env.example and tell the user what to set." >&2
    exit 2 ;;
esac
exit 0
