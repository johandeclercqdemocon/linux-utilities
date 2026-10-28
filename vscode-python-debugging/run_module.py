"""Run the file an editor hands you as a module, rooted at its project.

VS Code's "current file" debug configuration passes a *path*, and debugpy then
runs that path as a script. A file inside a package that imports its siblings
relatively dies immediately:

    ImportError: attempted relative import with no known parent package

and the message points nowhere near the cause. Even without relative imports
the two differ: running a file as a script puts *that file's* directory on
sys.path and leaves __package__ unset, while `-m` puts the project root there.

This converts the path into a dotted module name and hands it to runpy, so
pressing F5 does what `python -m package.module` does.

    python -m run_module path/to/file.py [args...]

The project root is found by walking up from the file for pyproject.toml,
setup.py, setup.cfg or .git. A file with no such ancestor, or one whose root is
not importable, is run as a plain script — which is what you wanted for a
scratch file in /tmp.
"""

from __future__ import annotations

import pathlib
import runpy
import sys

MARKERS = ("pyproject.toml", "setup.py", "setup.cfg", ".git")


def project_root(target: pathlib.Path) -> pathlib.Path | None:
    """The nearest ancestor that looks like the top of a project."""
    for directory in target.resolve().parents:
        if any((directory / marker).exists() for marker in MARKERS):
            return directory
    return None


def module_name(target: pathlib.Path, root: pathlib.Path) -> str | None:
    """`<root>/pkg/mod.py` -> `pkg.mod`, or None if that cannot be formed.

    A package's `__main__.py` becomes the package itself, because that is what
    `-m` means for a package.
    """
    try:
        relative = target.resolve().relative_to(root)
    except ValueError:
        return None
    if relative.suffix != ".py":
        return None
    parts = list(relative.with_suffix("").parts)
    if parts and parts[-1] == "__main__":
        parts.pop()
    return ".".join(parts) if parts else None


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: python -m run_module <file.py> [args...]", file=sys.stderr)
        return 2

    target = pathlib.Path(argv[0])
    if not target.exists():
        print(f"no such file: {target}", file=sys.stderr)
        return 2

    root = project_root(target)
    name = module_name(target, root) if root else None

    # argv must look the way it does under `python -m`: the script's own path
    # first, then whatever the caller passed after it.
    sys.argv = [str(target), *argv[1:]]

    if name is None:
        # No project, or not a .py file. Run it as a plain script, which is
        # both what the editor would have done and what the author intended.
        runpy.run_path(str(target), run_name="__main__")
        return 0

    # Importing by name needs the root on the path. It usually already is,
    # because the debugger's cwd is the project folder, but not when the file
    # being debugged belongs to a different project than the open workspace.
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    runpy.run_module(name, run_name="__main__", alter_sys=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
