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
import traceback
import time
import numpy as np

# Add tg_scripting to path
CHART_PLATFORM = os.path.expanduser("~/StudioProjects/chart-platform")
TG_PKG = os.path.join(CHART_PLATFORM, "website/public/scripts/pyodide-packages")
sys.path.insert(0, TG_PKG)

from tg_scripting.context import ScriptContext

MARKETPLACE_ROOT = os.path.dirname(os.path.abspath(__file__))


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
    """Run a single script through ScriptContext. Returns (success, error_msg)."""
    try:
        with open(script_path, "r") as f:
            source = f.read()

        # Compile first (syntax check)
        compile(source, script_path, "exec")

        # Execute with mock data
        bars = make_mock_bars()
        ctx = ScriptContext(bars)
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
    for kind, pyname in [("indicators", "indicator.py"), ("strategies", "strategy.py")]:
        pattern = os.path.join(MARKETPLACE_ROOT, kind, "*", pyname)
        for path in sorted(glob.glob(pattern)):
            rel = os.path.relpath(path, MARKETPLACE_ROOT)
            folder = os.path.dirname(rel)
            if filter_path and filter_path not in folder:
                continue
            scripts.append((folder, path))
    return scripts


def main():
    filter_path = sys.argv[1] if len(sys.argv) > 1 else None
    scripts = find_all_scripts(filter_path)

    if not scripts:
        print("No scripts found.")
        return 1

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
        return 1

    print("All scripts validated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
