#!/usr/bin/env python3
"""Self-checking tests for the built-in name generator (D-062).

This repo has no test harness -- no tests/, no conftest.py, no pytest config --
so this file is a plain script that runs itself:

    python tools/test_generate_builtin_names.py

The function names are pytest-compatible, so it also runs under pytest if one
is ever added, without changing anything here.
"""

import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import generate_builtin_names as g  # noqa: E402

GENERATOR = os.path.join(HERE, "generate_builtin_names.py")

ONE_LINE = """export const CATALOG = [
  { name: 'SMA', label: 'Simple Moving Average', pane: 'overlay' },
  { name: 'RSI', label: 'Relative Strength Index', pane: 'oscillator' },
];
"""

WRAPPED = """export const CATALOG = [
  {
    name: 'SMA',
    label: 'Simple Moving Average',
    pane: 'overlay',
  },
  { name: 'RSI', label: 'Relative Strength Index', pane: 'oscillator' },
];
"""

WRAPPED_DISABLED = """export const CATALOG = [
  {
    name: 'SMA',
    label: 'Simple Moving Average',
    disabled: true,
  },
  { name: 'RSI', label: 'Relative Strength Index', pane: 'oscillator' },
];
"""


def _write(tmp, text, name="catalog.ts"):
    path = os.path.join(tmp, name)
    with open(path, "w") as f:
        f.write(text)
    return path


def test_wrapped_row_is_still_extracted():
    """A row reformatted over three lines must not vanish from the snapshot."""
    with tempfile.TemporaryDirectory() as tmp:
        flat = g.extract(_write(tmp, ONE_LINE, "flat.ts"))
        wrapped = g.extract(_write(tmp, WRAPPED, "wrapped.ts"))
    assert flat == (["RSI", "SMA"], ["Relative Strength Index", "Simple Moving Average"]), flat
    assert wrapped == flat, f"wrapped row dropped out: {wrapped} != {flat}"


def test_disabled_row_is_still_skipped_when_wrapped():
    """`disabled: true` on its own line still excludes the row."""
    with tempfile.TemporaryDirectory() as tmp:
        names, labels = g.extract(_write(tmp, WRAPPED_DISABLED))
    assert names == ["RSI"], names
    assert labels == ["Relative Strength Index"], labels


def _run(catalog_path, out_path, *args):
    env = dict(os.environ)
    env["TG_CATALOG_PATH"] = catalog_path
    env["TG_BUILTIN_NAMES_OUT"] = out_path
    return subprocess.run(
        [sys.executable, GENERATOR, *args], cwd=HERE, env=env,
        capture_output=True, text=True,
    )


def test_shrink_is_refused_without_the_flag():
    """Losing a name must fail the generator, not quietly rewrite the snapshot."""
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "builtin-names.json")
        full = _write(tmp, ONE_LINE, "full.ts")
        assert _run(full, out).returncode == 0
        before = json.load(open(out))
        assert before["names"] == ["RSI", "SMA"], before["names"]

        # Now remove a name from the catalog fixture.
        reduced = _write(tmp, ONE_LINE.replace(
            "  { name: 'SMA', label: 'Simple Moving Average', pane: 'overlay' },\n", ""
        ), "reduced.ts")

        blocked = _run(reduced, out)
        assert blocked.returncode != 0, blocked.stdout
        assert "SHRANK" in blocked.stdout, blocked.stdout
        assert "'SMA'" in blocked.stdout, blocked.stdout
        assert json.load(open(out))["names"] == ["RSI", "SMA"], "snapshot was written anyway"

        allowed = _run(reduced, out, "--allow-shrink")
        assert allowed.returncode == 0, allowed.stdout + allowed.stderr
        assert json.load(open(out))["names"] == ["RSI"], "snapshot was not written"


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
