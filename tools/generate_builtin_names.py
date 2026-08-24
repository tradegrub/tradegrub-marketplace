#!/usr/bin/env python3
"""Regenerate builtin-names.json from the chart platform's indicator catalog.

The catalog lives in the private chart-platform repo and is the single source
of truth for what ships built in:

    charting-library/ui/src/components/indicator-catalog.ts

Every catalog row is one line of the form `{ name: '...', label: '...', ... }`.
We take the DISTINCT `name` and `label` of every row that is NOT
`disabled: true`. Rows also carry `variants` (SMA 20/50/100/200), which expand
into several picker rows off a single name -- so the raw count of `{ name:`
lines (452 at time of writing) is much larger than the number of distinct
built-ins.

Both `name` and `label` are collected because they are different things: `name`
is the registration key core uses (`SMA`, `Linear Regression`) and `label` is
what a user reads in the picker (`Simple Moving Average`). A marketplace
submission may collide with either, so the duplicate gate checks both.

Usage:
    python tools/generate_builtin_names.py            # writes builtin-names.json
    python tools/generate_builtin_names.py --check    # exit 1 if stale

Set TG_CHART_PLATFORM to point at a chart-platform checkout other than
~/StudioProjects/chart-platform.
"""

import json
import os
import re
import sys

# The catalog lives in a different (private) repo. Default to the usual sibling
# checkout, but let a caller point at its own checkout so the drift test in
# chart-platform can run against the tree it is actually testing.
CHART_PLATFORM = os.environ.get(
    "TG_CHART_PLATFORM", os.path.expanduser("~/StudioProjects/chart-platform")
)
CATALOG = os.path.join(
    CHART_PLATFORM, "charting-library/ui/src/components/indicator-catalog.ts"
)
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "builtin-names.json")

ROW = re.compile(r"^\s*\{ name: '((?:[^'\\]|\\.)*)'")
LABEL = re.compile(r"label: '((?:[^'\\]|\\.)*)'|label: \"((?:[^\"\\]|\\.)*)\"")


def extract(catalog_path=CATALOG):
    names, labels = set(), set()
    with open(catalog_path) as f:
        for line in f:
            m = ROW.match(line)
            if not m:
                continue
            if "disabled: true" in line:
                continue
            names.add(m.group(1).replace("\\'", "'"))
            lm = LABEL.search(line)
            if lm:
                labels.add((lm.group(1) or lm.group(2)).replace("\\'", "'"))
    return sorted(names), sorted(labels)


def build(catalog_path=CATALOG):
    names, labels = extract(catalog_path)
    return {
        "_comment": (
            "Generated -- do not hand-edit. Run tools/generate_builtin_names.py "
            "against a checkout of the chart-platform repo to regenerate. Source: "
            "charting-library/ui/src/components/indicator-catalog.ts, distinct "
            "name/label of every row without disabled: true."
        ),
        "source": "charting-library/ui/src/components/indicator-catalog.ts",
        "generator": "tools/generate_builtin_names.py",
        "names": names,
        "labels": labels,
    }


def _drift(current_data, fresh_data):
    """Name what changed, so the failure is actionable rather than "stale"."""
    lines = []
    for field in ("names", "labels"):
        was = set(current_data.get(field, []))
        now = set(fresh_data.get(field, []))
        for added in sorted(now - was):
            lines.append(f"  + {field[:-1]} missing from snapshot: {added!r}")
        for removed in sorted(was - now):
            lines.append(f"  - {field[:-1]} in snapshot but no longer built in: {removed!r}")
    return lines


def main():
    if not os.path.exists(CATALOG):
        print(f"Catalog not found: {CATALOG}")
        print("Set TG_CHART_PLATFORM to a chart-platform checkout.")
        return 2

    data = build()
    text = json.dumps(data, indent=2) + "\n"
    if "--check" in sys.argv:
        current = open(OUT).read() if os.path.exists(OUT) else ""
        if current != text:
            print("builtin-names.json is STALE: it no longer matches")
            print(f"  {data['source']}")
            try:
                lines = _drift(json.loads(current), data)
            except ValueError:
                lines = ["  (existing builtin-names.json is not valid JSON)"]
            for line in lines or ["  (metadata changed)"]:
                print(line)
            print("\nA stale snapshot means a marketplace item can duplicate a NEW")
            print("built-in and pass the duplicate gate. Regenerate it:")
            print("\n  cd ~/StudioProjects/tradegrub-marketplace \\")
            print("    && /Users/vw/venv/bin/python tools/generate_builtin_names.py\n")
            return 1
        print("builtin-names.json is current.")
        return 0
    with open(OUT, "w") as f:
        f.write(text)
    print(f"Wrote {OUT}: {len(data['names'])} names, {len(data['labels'])} labels")
    return 0


if __name__ == "__main__":
    sys.exit(main())
