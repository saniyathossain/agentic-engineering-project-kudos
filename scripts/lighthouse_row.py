"""Print one markdown table row for a Lighthouse JSON report. Usage: lighthouse_row.py <report.json> <page> <form> <theme>."""
import json
import sys


def score(categories: dict, key: str) -> str:
    value = categories[key]["score"]
    return "n/a" if value is None else str(round(value * 100))


def metric(audits: dict, key: str) -> str:
    return audits[key].get("displayValue", "n/a").replace(" ", " ")


path, page, form, theme = sys.argv[1:5]
try:
    with open(path) as handle:
        report = json.load(handle)
    c, a = report["categories"], report["audits"]
    print(
        f"| {page} | {form} | {theme} | {score(c, 'performance')} | {score(c, 'accessibility')} | {score(c, 'best-practices')} | {score(c, 'seo')} "
        f"| {metric(a, 'first-contentful-paint')} | {metric(a, 'largest-contentful-paint')} | {metric(a, 'total-blocking-time')} | {metric(a, 'cumulative-layout-shift')} |"
    )
except (OSError, KeyError, ValueError):
    print(f"| {page} | {form} | {theme} | failed | failed | failed | failed | - | - | - | - |")
