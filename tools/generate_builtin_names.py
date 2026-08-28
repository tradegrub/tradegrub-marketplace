#!/usr/bin/env python3
"""Regenerate builtin-names.json from the chart platform's indicator catalog.

The catalog lives in the private chart-platform repo and is the single source
of truth for what ships built in:

    charting-library/ui/src/components/indicator-catalog.ts

Every catalog row has the form `{ name: '...', label: '...', ... }`. Rows are
matched across the whole file, not line by line, so a row wrapped over several
lines is still picked up; and the generator refuses to write a snapshot that
covers fewer names than the one already on disk.
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
    python tools/generate_builtin_names.py --allow-shrink  # accept a smaller set

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
# TG_CATALOG_PATH and TG_BUILTIN_NAMES_OUT exist so the generator can be driven
# against fixtures (tools/test_generate_builtin_names.py) without touching either
# real file.
CATALOG = os.environ.get("TG_CATALOG_PATH") or os.path.join(
    CHART_PLATFORM, "charting-library/ui/src/components/indicator-catalog.ts"
)
OUT = os.environ.get("TG_BUILTIN_NAMES_OUT") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "builtin-names.json")

ROW = re.compile(r"\{\s*name:\s*'((?:[^'\\]|\\.)*)'")
LABEL = re.compile(r"label: '((?:[^'\\]|\\.)*)'|label: \"((?:[^\"\\]|\\.)*)\"")


def _row_text(text, open_idx):
    """Return the source of one catalog row, from its `{` to the matching `}`.

    Rows are matched against the whole file rather than line by line: whether a
    row sits on one line or is wrapped over several is only a formatting choice
    in indicator-catalog.ts, and a line-anchored regex silently drops the
    wrapped ones out of the snapshot (D-062). Brace matching is quote-aware so
    a `}` inside a string does not close the row early.
    """
    depth = 0
    quote = None
    i = open_idx
    while i < len(text):
        c = text[i]
        if quote:
            if c == "\\":
                i += 2
                continue
            if c == quote:
                quote = None
        elif c in "'\"`":
            quote = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[open_idx:i + 1]
        i += 1
    return text[open_idx:]


def extract(catalog_path=CATALOG):
    names, labels = set(), set()
    with open(catalog_path) as f:
        text = f.read()
    for m in ROW.finditer(text):
        row = _row_text(text, m.start())
        if "disabled: true" in row:
            continue
        names.add(m.group(1).replace("\\'", "'"))
        lm = LABEL.search(row)
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


def _shrink(fresh_data, out_path=OUT):
    """Report any field where the fresh extraction covers LESS than the snapshot.

    The generator is the only thing that writes builtin-names.json, so a bug in
    the extractor -- or a catalog row it stopped matching -- would otherwise be
    laundered into a smaller, still-green gate by the very regeneration the
    drift test asks for (D-062). Losing a name is therefore a failure that has
    to be asserted, not a diff to be accepted.
    """
    if not os.path.exists(out_path):
        return []
    try:
        with open(out_path) as f:
            previous = json.load(f)
    except (ValueError, OSError):
        return []
    lines = []
    for field in ("names", "labels"):
        was = set(previous.get(field, []))
        now = set(fresh_data.get(field, []))
        lost = sorted(was - now)
        if lost:
            lines.append(
                f"{field}: {len(was)} -> {len(now)} ({len(lost)} lost)"
            )
            lines.extend(f"    - {item!r}" for item in lost[:20])
            if len(lost) > 20:
                lines.append(f"    ... and {len(lost) - 20} more")
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
    shrink = _shrink(data, OUT)
    if shrink and "--allow-shrink" not in sys.argv:
        print("REFUSING to write builtin-names.json: the extracted set SHRANK.\n")
        for line in shrink:
            print(f"  {line}")
        print("\nA smaller snapshot means the duplicate gate protects FEWER")
        print("built-ins than before, and every check then reads green while")
        print("covering less. Either the catalog really lost those rows, or the")
        print("extractor stopped matching them -- find out which before writing.")
        print("\nIf the removal is intended, re-run with --allow-shrink.\n")
        return 1

    with open(OUT, "w") as f:
        f.write(text)
    print(f"Wrote {OUT}: {len(data['names'])} names, {len(data['labels'])} labels")
    return 0


if __name__ == "__main__":
    sys.exit(main())
