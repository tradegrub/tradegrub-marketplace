#!/usr/bin/env python3
"""Compile-and-run gate for marketplace scripts.

Executes every indicator/strategy Python script against synthetic OHLCV data
using the real tg_scripting runtime. Any script that raises an exception fails
the gate and blocks publishing.

Usage:
    python validate_scripts.py                # validate all scripts
    python validate_scripts.py strategies/wedge-breakout  # validate one
"""

import sys
import os
import json
import glob
import re
import traceback
import time
import numpy as np

# Add tg_scripting to path
CHART_PLATFORM = os.path.expanduser("~/StudioProjects/chart-platform")
TG_PKG = os.path.join(CHART_PLATFORM, "website/public/scripts/pyodide-packages")
sys.path.insert(0, TG_PKG)

from tg_scripting.context import ScriptContext

MARKETPLACE_ROOT = os.path.dirname(os.path.abspath(__file__))

# Every (folder, filename) pair that counts as a publishable script. Pine sits
# alongside Python because some scripts -- the fundamental scores in
# particular -- need request.financial(), which only the Pine runtime exposes.
SCRIPT_FILES = [
    ("indicators", "indicator.py"),
    ("indicators", "indicator.pine"),
    ("strategies", "strategy.py"),
    ("strategies", "strategy.pine"),
]


def make_mock_bars(n=200):
    """Generate realistic synthetic OHLCV bars."""
    np.random.seed(42)
    base = 100.0
    prices = [base]
    for _ in range(n - 1):
        prices.append(prices[-1] * (1 + np.random.normal(0, 0.02)))
    bars = []
    t = 1700000000000
    for i, p in enumerate(prices):
        h = p * (1 + abs(np.random.normal(0, 0.005)))
        l = p * (1 - abs(np.random.normal(0, 0.005)))
        o = p * (1 + np.random.normal(0, 0.003))
        v = max(1000, int(np.random.normal(1_000_000, 300_000)))
        bars.append({"time": t + i * 86400000, "open": o, "high": h, "low": l, "close": p, "volume": v})
    return bars


def validate_script(script_path):
    """Run a single script through ScriptContext. Returns (success, error_msg).

    Pine scripts go through the Pine interpreter instead of exec(). They are
    held to the same bar: parse and run against synthetic OHLCV without
    raising. Fundamental scripts see no financial data in this harness, which
    is deliberate -- a script that blows up on missing fundamentals would blow
    up the same way on a crypto pair.
    """
    try:
        with open(script_path, "r") as f:
            source = f.read()

        bars = make_mock_bars()
        ctx = ScriptContext(bars)

        if script_path.endswith(".pine"):
            from tg_scripting.pine import interpreter as pine
            pine.interpret(source, ctx)
            return True, None

        # Compile first (syntax check)
        compile(source, script_path, "exec")

        ns = ctx.build_namespace()

        # Add numpy and common imports
        ns["__builtins__"] = __builtins__
        exec(source, ns)

        return True, None
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def find_all_scripts(filter_path=None):
    """Find all marketplace script files."""
    scripts = []
    for kind, fname in SCRIPT_FILES:
        pattern = os.path.join(MARKETPLACE_ROOT, kind, "*", fname)
        for path in sorted(glob.glob(pattern)):
            rel = os.path.relpath(path, MARKETPLACE_ROOT)
            folder = os.path.dirname(rel)
            if filter_path and filter_path not in folder:
                continue
            scripts.append((folder, path))
    return scripts


def check_index_parity():
    """Every script folder must have an index.json entry, and vice versa.

    index.json is maintained by hand (see CONTRIBUTING.md), and the app reads
    ONLY that file -- it never lists the repo. So a folder missing from the
    index is a script that exists, passes this gate, and is invisible to every
    user. That is exactly how 11 scripts went unpublished from the initial
    commit until 2026-07-31 without anything failing.

    The app resolves a folder as (strategies|indicators)/<id> keyed off `type`,
    so an id may legitimately appear twice -- once as an indicator and once as
    a strategy. Parity is therefore checked on (type-folder, id), not id alone.

    Returns a list of human-readable problems; empty means the index is honest.
    """
    index_path = os.path.join(MARKETPLACE_ROOT, "index.json")
    with open(index_path) as f:
        entries = json.load(f)

    indexed = set()
    problems = []
    for e in entries:
        kind = "strategies" if e.get("type") == "strategy" else "indicators"
        key = (kind, e.get("id"))
        if key in indexed:
            problems.append(f"index.json lists {kind}/{e.get('id')} more than once")
        indexed.add(key)

    on_disk = {
        (kind, os.path.basename(os.path.dirname(path)))
        for kind, path in (
            (k, p)
            for k, fname in SCRIPT_FILES
            for p in glob.glob(os.path.join(MARKETPLACE_ROOT, k, "*", fname))
        )
    }

    for kind, sid in sorted(on_disk - indexed):
        problems.append(f"{kind}/{sid} exists on disk but is NOT in index.json (invisible in-app)")
    for kind, sid in sorted(indexed - on_disk):
        problems.append(f"{kind}/{sid} is in index.json but has no folder (broken install)")
    return problems


def _normalize_name(name):
    """Fold a display name to its comparison key.

    Case, whitespace and punctuation are all noise for this rule: "Zero-Lag
    EMA", "zero lag ema" and "Zero_Lag_EMA" are the same indicator to a user
    browsing the picker. So the key is the lowercased name with every
    non-alphanumeric character removed.
    """
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _readme_title(folder):
    """The first markdown H1 in the folder's README, if any."""
    for candidate in ("README.md", "readme.md"):
        path = os.path.join(folder, candidate)
        if not os.path.exists(path):
            continue
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("# "):
                        return line[2:].strip()
        except OSError:
            return None
    return None


def check_builtin_duplicates(only=None):
    """No marketplace item may duplicate a predefined built-in.

    CONTRIBUTING.md has carried this rule as a review checkbox since the repo
    opened, which meant it held exactly as well as a reviewer's memory: eight
    duplicates shipped and were removed by hand in July 2026.

    builtin-names.json is the checked-in list of built-in names and picker
    labels, generated from the chart platform's indicator-catalog.ts by
    tools/generate_builtin_names.py. Both fields matter -- `name` is the
    registration key ("SMA") and `label` is what the user reads ("Simple
    Moving Average") -- so a submission colliding with either is a duplicate.

    The manifest `name` is not the only place the collision can hide: the
    folder id, the README H1 and the index.json name are all read by a user or
    the app, so all four are checked and the failure names which one collided.

    `only` scopes the check to a set of (kind, id) pairs, so validating a
    single script still runs this gate on that script.

    Returns a list of human-readable problems; empty means nothing collides.
    """
    names_path = os.path.join(MARKETPLACE_ROOT, "builtin-names.json")
    if not os.path.exists(names_path):
        return ["builtin-names.json is missing; run tools/generate_builtin_names.py"]

    with open(names_path) as f:
        data = json.load(f)

    builtin = {}
    for original in list(data.get("names", [])) + list(data.get("labels", [])):
        builtin.setdefault(_normalize_name(original), set()).add(original)

    index_names = {}
    index_path = os.path.join(MARKETPLACE_ROOT, "index.json")
    if os.path.exists(index_path):
        try:
            with open(index_path) as f:
                for e in json.load(f):
                    ekind = "strategies" if e.get("type") == "strategy" else "indicators"
                    index_names[(ekind, e.get("id"))] = (e.get("name") or "").strip()
        except ValueError:
            pass

    problems = []
    for kind in ("indicators", "strategies"):
        for manifest_path in sorted(glob.glob(os.path.join(MARKETPLACE_ROOT, kind, "*", "manifest.json"))):
            sid = os.path.basename(os.path.dirname(manifest_path))
            if only and (kind, sid) not in only:
                continue
            try:
                with open(manifest_path) as f:
                    manifest = json.load(f)
            except ValueError as e:
                problems.append(f"{kind}/{sid}: manifest.json is not valid JSON ({e})")
                continue
            name = (manifest.get("name") or "").strip()
            if not name:
                problems.append(f"{kind}/{sid}: manifest.json has no name")
                continue

            # Every field a user or the app can read the item's identity from.
            # Checking manifest.name alone let "Ultra EMA" ship in a folder
            # called `ema` and read as the built-in everywhere the id shows
            # (D-063). The field that collided is named in the message,
            # because a gate nobody can act on gets ignored.
            candidates = [
                ("manifest.json name", name),
                ("folder id", sid),
                ("README title", _readme_title(os.path.dirname(manifest_path))),
                ("index.json name", index_names.get((kind, sid))),
            ]
            for field, value in candidates:
                if not value:
                    continue
                hit = builtin.get(_normalize_name(value))
                if hit:
                    problems.append(
                        f"{kind}/{sid}: {field} \"{value}\" duplicates built-in "
                        f"{' / '.join(sorted(hit))} -- rename it or withdraw it"
                    )
    return problems


def main():
    filter_path = sys.argv[1] if len(sys.argv) > 1 else None
    scripts = find_all_scripts(filter_path)

    if not scripts:
        print("No scripts found.")
        return 1

    # Parity is a whole-repo property, so only assert it on a full run.
    index_problems = [] if filter_path else check_index_parity()
    # Duplication is a per-item property, so it runs on a filtered path too,
    # scoped to the scripts that were selected. Skipping it there removed the
    # gate at the exact moment a contributor checks their own submission
    # (D-064).
    only = None
    if filter_path:
        only = {
            (folder.split(os.sep)[0], os.path.basename(folder))
            for folder, _ in scripts
        }
    duplicate_problems = check_builtin_duplicates(only)

    passed = 0
    failed = 0
    errors = []

    print(f"\nValidating {len(scripts)} marketplace scripts...\n")
    print(f"{'Script':<45} {'Status':<10} {'Time':>8}")
    print("-" * 65)

    for folder, path in scripts:
        start = time.time()
        ok, err = validate_script(path)
        elapsed = time.time() - start

        if ok:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"
            errors.append((folder, err))

        print(f"{folder:<45} {status:<10} {elapsed:>7.2f}s")

    print("-" * 65)
    print(f"\nTotal: {len(scripts)} | Passed: {passed} | Failed: {failed}\n")

    if errors:
        print("FAILURES:\n")
        for folder, err in errors:
            print(f"  {folder}")
            print(f"    {err}\n")

    if index_problems:
        print("INDEX PARITY FAILURES:\n")
        for p in index_problems:
            print(f"  {p}")
        print("\n  index.json is what the app reads. A script missing from it "
              "ships to nobody.\n")

    if duplicate_problems:
        print("BUILT-IN DUPLICATE FAILURES:\n")
        for p in duplicate_problems:
            print(f"  {p}")
        print("\n  A marketplace item that shadows a built-in gives users two "
              "rows for one indicator.\n")

    if errors or index_problems or duplicate_problems:
        return 1

    print("All scripts validated successfully; index.json matches the tree.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
