#!/usr/bin/env python3
"""Merge a partial translation file into lang/en.json, safely when several writers run at once.

    python3 scripts/lang_add.py path/to/partial.json

Keys are flat and dotted ("spaces.index.title"). An existing key with identical text is fine; an existing key
with different text is an error (pick another key). The file is rewritten atomically under a lock, keys sorted.
"""
import fcntl
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, 'lang', 'en.json')
LOCK = os.path.join(ROOT, 'lang', '.lang.lock')


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    with open(sys.argv[1], encoding='utf-8') as handle:
        incoming = json.load(handle)
    if not isinstance(incoming, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in incoming.items()):
        print('partial must be a flat JSON object of string keys and string values')
        return 2

    with open(LOCK, 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        with open(TARGET, encoding='utf-8') as handle:
            current = json.load(handle)
        clashes = [k for k, v in incoming.items() if k in current and current[k] != v]
        if clashes:
            print('keys already exist with different text:', ', '.join(clashes))
            return 1
        added = [k for k in incoming if k not in current]
        current.update(incoming)
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(TARGET), suffix='.json')
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            json.dump(dict(sorted(current.items())), out, indent=4, ensure_ascii=False)
            out.write('\n')
        os.chmod(tmp, 0o644)  # mkstemp creates 0600; php-fpm in the prod image must be able to read the file
        os.replace(tmp, TARGET)
    print(f'added {len(added)} keys, {len(incoming) - len(added)} already present')
    return 0


if __name__ == '__main__':
    sys.exit(main())
