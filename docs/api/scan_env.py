"""Finds every env('NAME', default) call in the app's PHP config, bootstrap and app code (balanced-paren scan)."""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]


def scan():
    found = {}
    pat = re.compile(r"\benv\(\s*'([A-Z][A-Z0-9_]*)'")
    for base in ("codes/config", "codes/bootstrap", "codes/app"):
        for f in sorted((ROOT / base).rglob("*.php")):
            if "bootstrap/cache" in str(f):
                continue
            text = f.read_text()
            for m in pat.finditer(text):
                i, depth, j = m.end(), 1, m.end()
                while j < len(text) and depth:
                    depth += {"(": 1, ")": -1}.get(text[j], 0)
                    j += 1
                args = text[m.start() + 4:j - 1]  # inside env( ... )
                default = args.split(",", 1)[1].strip() if "," in args else None
                found.setdefault(m.group(1), []).append((str(f.relative_to(ROOT)), default))
    return found


if __name__ == "__main__":
    for k, v in sorted(scan().items()):
        print(k, v[0])
