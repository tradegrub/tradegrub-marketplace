#!/usr/bin/env python3
"""Self-checking tests for the in-script title duplicate check (D-068).

This repo has no test harness -- no tests/, no conftest.py, no pytest config --
so this file is a plain script that runs itself, matching
tools/test_generate_builtin_names.py:

    python tools/test_script_title_check.py

The function names are pytest-compatible, so it also runs under pytest if one
is ever added.
"""

import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import validate_scripts as v  # noqa: E402


def _title(source, ext=".py"):
    """Run a source snippet through the folder-level title reader."""
    folder = tempfile.mkdtemp()
    try:
        with open(os.path.join(folder, "indicator" + ext), "w") as f:
            f.write(source)
        return v._script_declared_title(folder)
    finally:
        shutil.rmtree(folder)


def test_python_first_positional():
    assert _title('indicator("Trend Strength", overlay=True)') == "Trend Strength"


def test_python_single_quotes():
    assert _title("indicator('Price Channel', overlay=True)") == "Price Channel"


def test_python_title_keyword():
    assert _title('indicator(title="Keyword Title", overlay=False)') == "Keyword Title"


def test_python_multiline_call():
    src = 'indicator(\n    "Wrapped Title",\n    overlay=True,\n)'
    assert _title(src) == "Wrapped Title"


def test_python_strategy_call():
    assert _title('strategy("Some Strategy")') == "Some Strategy"


def test_python_computed_title_is_not_guessed():
    # A runtime-built title cannot be checked statically, and the scripts are
    # never executed to find out. Absent beats wrong.
    assert _title('name = "X"\nindicator(name, overlay=True)') is None


def test_python_syntax_error_is_left_to_the_run_gate():
    assert _title('indicator("Broken", ') is None


def test_pine_first_positional():
    assert _title('//@version=6\nindicator("Pine Title", overlay=true)', ".pine") == "Pine Title"


def test_pine_title_keyword_across_lines():
    src = '//@version=6\nstrategy(\n  title="Pine Kw",\n  overlay=false)'
    assert _title(src, ".pine") == "Pine Kw"


def test_pine_comma_inside_the_title_is_not_a_separator():
    src = '//@version=6\nindicator("Cup, and Handle", overlay=true)'
    assert _title(src, ".pine") == "Cup, and Handle"


def test_pine_commented_out_call_is_skipped():
    src = '//@version=6\n// indicator("Commented")\nindicator("Real One")'
    assert _title(src, ".pine") == "Real One"


def test_pine_call_named_inside_a_string_is_skipped():
    src = '//@version=6\nx = "see indicator(\\"Fake\\")"\nindicator("Real One")'
    assert _title(src, ".pine") == "Real One"


def test_colliding_script_title_is_reported_with_its_field():
    """The whole point of D-068: a clean manifest hiding a built-in title."""
    root = tempfile.mkdtemp()
    old_root = v.MARKETPLACE_ROOT
    try:
        v.MARKETPLACE_ROOT = root
        folder = os.path.join(root, "indicators", "multi-factor-thing")
        os.makedirs(folder)
        with open(os.path.join(root, "builtin-names.json"), "w") as f:
            json.dump({"names": ["Trend Strength"], "labels": []}, f)
        with open(os.path.join(folder, "manifest.json"), "w") as f:
            json.dump({"name": "Multi-Factor Thing"}, f)
        with open(os.path.join(folder, "indicator.py"), "w") as f:
            f.write('indicator("Trend Strength", overlay=True)')

        problems = v.check_builtin_duplicates()
        assert len(problems) == 1, problems
        assert "script title" in problems[0], problems[0]
        assert "Trend Strength" in problems[0], problems[0]
    finally:
        v.MARKETPLACE_ROOT = old_root
        shutil.rmtree(root)


def test_clean_script_title_passes():
    root = tempfile.mkdtemp()
    old_root = v.MARKETPLACE_ROOT
    try:
        v.MARKETPLACE_ROOT = root
        folder = os.path.join(root, "indicators", "multi-factor-thing")
        os.makedirs(folder)
        with open(os.path.join(root, "builtin-names.json"), "w") as f:
            json.dump({"names": ["Trend Strength"], "labels": []}, f)
        with open(os.path.join(folder, "manifest.json"), "w") as f:
            json.dump({"name": "Multi-Factor Thing"}, f)
        with open(os.path.join(folder, "indicator.py"), "w") as f:
            f.write('indicator("Multi-Factor Thing", overlay=True)')

        assert v.check_builtin_duplicates() == []
    finally:
        v.MARKETPLACE_ROOT = old_root
        shutil.rmtree(root)


def test_cup_and_handle_raises_rather_than_finding_nothing():
    """D-070: the scipy fallback must not return a curvature that reads as a
    legitimate rejection. Parsed, not executed -- the script needs a runtime."""
    import ast

    path = os.path.join(
        os.path.dirname(HERE), "indicators", "cup-and-handle-curve-fit", "indicator.py"
    )
    tree = ast.parse(open(path).read())
    fn = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == "fit_score"
    )
    guard = fn.body[0]
    assert isinstance(guard, ast.If), "fit_score no longer opens with the scipy guard"
    assert any(isinstance(s, ast.Raise) for s in guard.body), \
        "the missing-scipy branch must raise, not return a silent 0.0 curvature"
    assert not any(isinstance(s, ast.Return) for s in guard.body), \
        "the missing-scipy branch still returns a value"


def main():
    tests = [v_ for k, v_ in sorted(globals().items()) if k.startswith("test_")]
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
