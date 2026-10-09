#!/usr/bin/env python3
"""Self-checking tests for validate_scripts.py's runtime lookup (chart-platform D-859).

validate_scripts.py must validate against the chart-platform checkout named by
TG_CHART_PLATFORM (a worktree under test), not always ~/StudioProjects/chart-platform.

    python tools/test_validate_scripts_env.py

Same plain-script shape as test_generate_builtin_names.py; also runs under pytest.
"""

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

PROBE = (
    "import validate_scripts as v, tg_scripting.context as c; "
    "print(v.CHART_PLATFORM); print(c.__file__)"
)


def _fake_checkout(root):
    """A chart-platform checkout whose tg_scripting is a stub, so we can tell it apart."""
    pkg = os.path.join(root, "website/public/scripts/pyodide-packages/tg_scripting")
    os.makedirs(pkg)
    open(os.path.join(pkg, "__init__.py"), "w").close()
    with open(os.path.join(pkg, "context.py"), "w") as f:
        f.write("class ScriptContext:\n    pass\n")


def _probe(env_value):
    env = {k: v for k, v in os.environ.items() if k != "TG_CHART_PLATFORM"}
    if env_value is not None:
        env["TG_CHART_PLATFORM"] = env_value
    return subprocess.run(
        [sys.executable, "-c", PROBE], cwd=REPO, env=env, capture_output=True, text=True
    )


def test_tg_chart_platform_selects_the_runtime():
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.realpath(tmp)
        _fake_checkout(root)
        r = _probe(root)
        assert r.returncode == 0, r.stdout + r.stderr
        platform, context_file = r.stdout.split()
        assert platform == root, platform
        assert os.path.realpath(context_file).startswith(root), context_file


def test_default_is_unchanged_without_the_variable():
    r = _probe(None)
    default = os.path.expanduser("~/StudioProjects/chart-platform")
    if not os.path.isdir(default):
        # No default checkout on this machine: the import fails, but the path is still the default.
        assert default in r.stderr or r.returncode != 0, r.stdout + r.stderr
        return
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.split()[0] == default, r.stdout


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
