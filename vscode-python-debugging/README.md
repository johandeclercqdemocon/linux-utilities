# vscode-python-debugging

Makes **F5 in VS Code do what `python -m package.module` does**, for any Python project.

Two files: a 92-line `run_module.py` with no dependencies, and a `launch.json` with three
configurations. Nothing to install.

## The problem it fixes

VS Code's obvious way to debug the open file is

```json
"program": "${file}"
```

which runs that file **as a script**. For a file inside a package that is not the same thing as
running it as a module.

## File mode and module mode, measured

The difference is easiest to see by printing it. One file, two invocations:

```python
# pkg/mod.py
import sys
print(f"  __name__    = {__name__!r}")
print(f"  __package__ = {__package__!r}")
print(f"  sys.path[0] = {sys.path[0]!r}")
```

with a `pkg/__init__.py` that prints one line when it is imported:

```text
=== as a FILE:  python pkg/mod.py
  __name__    = '__main__'
  __package__ = None
  sys.path[0] = '/tmp/proj/pkg'          <- the file's own folder

=== as a MODULE: python -m pkg.mod
  pkg/__init__.py ran                    <- the package was imported first
  __name__    = '__main__'
  __package__ = 'pkg'
  sys.path[0] = '/tmp/proj'              <- the project root
```

**File mode hands Python a path.** Python neither knows nor cares that the file belongs to a
package: it puts the file's own directory first on the import path and runs it.

**Module mode hands Python a name.** Python resolves it through the import system — current
directory first on the path, import `pkg` (running its `__init__.py`), then run `mod` inside it
with `__package__` set.

| | file mode (`"program"`) | module mode (`"module"` / `-m`) |
|---|---|---|
| first entry on `sys.path` | the file's own directory | the current directory |
| `__package__` | `None` | the package the file is in |
| the package's `__init__.py` | not run | run, before your code |
| `from .sibling import x` | **ImportError** | works |
| `__name__` | `'__main__'` | `'__main__'` |

Four consequences, in the order they bite:

1. **Relative imports.** `from .helper import VALUE` resolves against `__package__`. In file mode
   that is `None`, so it raises immediately. This is the big one; the rest are smaller.
2. **What your absolute imports find.** File mode puts `pkg/` on the path, so `import helper`
   works and `import pkg.helper` may not. Module mode is the other way round. Code that runs
   under both usually does so by accident.
3. **`__init__.py` runs in module mode only.** A package that registers something, configures
   logging or sets a backend there gets skipped silently in file mode, and you are debugging a
   subtly different program.
4. **`__name__` is `'__main__'` either way.** This is what makes the failure so confusing: the
   `if __name__ == "__main__":` guard fires in both modes, so the file looks like it is being run
   correctly right up until an import fails.

The rule: **if the file sits in a package, run it as a module.** For a standalone script with no
package around it the two are identical and file mode is fine.

## What goes wrong without this

A project where any module imports a sibling relatively has a Run button that cannot work:

```text
ImportError: attempted relative import with no known parent package
```

The message names the symptom, not the cause, and the usual reaction is to go looking at the
interpreter or the virtualenv — neither of which has anything to do with it. Worse, it is
*intermittent across a codebase*: the modules that happen to use absolute imports run fine, so
the Run button looks broken only for some files.

That is not a hypothetical. It shipped in a book of thirty-three chapters whose test suite was
green, because every check ran the code the way the book ran it — `python -m` from the project
root — and nobody was pressing the button.

## How it works

`run_module.py` takes the path VS Code hands it and turns it into a dotted module name:

1. Walk up from the file for `pyproject.toml`, `setup.py`, `setup.cfg` or `.git`. That ancestor
   is the project root.
2. `<root>/pkg/mod.py` becomes `pkg.mod`. A package's `__main__.py` becomes the package itself,
   because that is what `-m` means for a package.
3. Put the root on `sys.path` if it is not already there, then `runpy.run_module(name,
   run_name="__main__")`.
4. If no root is found, or the file sits outside it, run it as a plain script instead — which is
   the right answer for a scratch file in `/tmp`.

`sys.argv` is rewritten to look exactly as it does under `python -m`: the file's path first, then
anything you passed after it.

## Install

```bash
mkdir -p <project>/scripts <project>/.vscode
cp run_module.py <project>/scripts/
cp launch.json   <project>/.vscode/     # or merge the three entries into yours
```

Then edit `"module": "yourpackage.yourmodule"` in the first configuration, and you are done.

If you put `run_module.py` somewhere other than `scripts/`, change the second configuration's
`"module"` to match: it is a dotted path from the project root, so `tools/run_module.py` becomes
`"tools.run_module"`.

## The three configurations

**Module: the one I am working on** — always starts the same entry point, whichever file has
focus. Edit its `"module"` string once per task. Use it when you want to set a breakpoint deep in
a helper and still begin at the thing that produces output. Launching the helper itself usually
prints nothing, which is correct and confusing at the same moment.

**File: the one I am looking at** — no editing. Runs the active editor's file as a module, through
`run_module.py`. One visible cost: when you are paused, the **Call Stack** shows two extra frames
at the bottom —

```text
main         yourmodule.py    ...
<module>     yourmodule.py    ...
main         run_module.py    ...
<module>     run_module.py    ...
```

— which are the runner that launched it. They are harmless and always at the bottom, and VS Code
collapses them behind *Show 2 More Stack Frames*. Your code is everything above them.

**Tests: the file I am looking at** — runs `pytest <file> -q` under the debugger. Breakpoints work
in the test *and* in the library code it calls, which is the point: a failing assertion tells you
the value was wrong, and a breakpoint in the function that produced it tells you why. For a single
test, use the Test Explorer's right-click → *Debug Test* instead. Pointed at a file with no tests
it prints `no tests ran`, which is pytest being correct rather than a broken configuration.

## Standard debugging, which this does not change

If you have not used VS Code's debugger before, the loop is five steps and none of them are
specific to this utility.

1. **Open the file** you want to run.
2. **Set a breakpoint.** Click in the gutter left of a line number, or put the cursor on the line
   and press `F9`. A red dot appears. Put it on the line *after* the thing you want to inspect — a
   breakpoint stops *before* its own line runs.
3. **Start.** `F5`. The first time, VS Code asks which configuration; after that `F5` reuses the
   last one. The integrated terminal shows the command line it used.
4. **Look.** Execution stops at the dot. **Variables** on the left shows everything in scope.
   **Debug Console** at the bottom evaluates anything you type against the paused frame, which is
   where most of the value is: `len(rows)`, `df.columns.tolist()`, `config.timeout`. A `print`
   answers the question you thought to ask before you ran it; the console answers the one you
   thought of afterwards.
5. **Move.** `F10` steps over the current line, `F11` steps *into* the call on it, `Shift+F11`
   steps back out, `F5` continues to the next breakpoint, `Shift+F5` stops.

Two breakpoint types repay learning. A **conditional breakpoint** — right-click a breakpoint,
*Edit Breakpoint* — stops only when an expression is true, which is how you catch the one
iteration out of five hundred that misbehaves without stepping through the other 499. A
**logpoint** prints a message and does not stop at all: a `print` you cannot forget to delete.

## Debugging a plain script

A standalone file with no package around it — a scratch file, a one-off, anything you would
normally just run — needs none of this. With no package around it, the differences in the table
above have nothing to grip on: there are no relative imports to resolve, no `__init__.py` to skip,
and running it from its own directory gives the same `sys.path[0]` either way. The only visible
difference is cosmetic — `__package__` is `None` as a file and `''` as a module, both falsy.

So three things all work:

- **File: the one I am looking at.** The runner finds no project, or finds one the file is not
  inside, and runs it as a plain script. `__name__` is `"__main__"` and `sys.argv[0]` is your
  file, so a main guard fires normally.
- **Python Debugger: Debug Python File**, contributed by the Python extension and offered in the
  dropdown. Equivalent here, and the right choice in a project with no `launch.json` at all.
- **The ▷ Run button's dropdown → Debug Python File**, which is the same thing from the editor
  toolbar.

So the only question this utility answers is the one that arises when the file is *inside a
package*. Everything else about debugging is unchanged, which is the point: it removes a failure
mode rather than adding a workflow.

## `"justMyCode": false`

All three set it. Left at its default of `true`, the debugger silently refuses to step into
installed packages — F11 runs straight past the call you wanted to watch, with no message saying
why. If you are debugging to find out what a library actually did, rather than what its
documentation says it did, this line is the whole point.

## Verifying it

The failure and the fix, end to end:

```bash
mkdir -p /tmp/proj/pkg && cd /tmp/proj && touch pyproject.toml pkg/__init__.py
echo 'VALUE = 42' > pkg/helper.py
printf 'from .helper import VALUE\n\nif __name__ == "__main__":\n    print("worked, VALUE =", VALUE)\n' > pkg/main.py

python3 pkg/main.py
# ImportError: attempted relative import with no known parent package

python3 ~/claude/utilities/vscode-python-debugging/run_module.py pkg/main.py
# worked, VALUE = 42
```

## Notes

- Standard library only — `pathlib`, `runpy`, `sys`. No extension, no package, nothing to keep
  updated. `from __future__ import annotations` carries the type hints, so there is no syntax
  here newer than 3.7; tested on 3.12.3 and 3.13.12, which are the two on this machine.
- The Python extension contributes its own **Python Debugger: Debug Python File**. That one uses
  the file path directly, so it has the behaviour described at the top. It is fine for a
  standalone script and the right choice in a project with no `launch.json`.
- The problem was found in `~/claude/ml-book`, which ships its own earlier copy at
  `scripts/run_module.py`. That one is deliberately simpler — it assumes it sits in
  `<root>/scripts/` and takes the root from its own location, rather than discovering it — and its
  chapter quotes its line numbers, so it is pinned. **This is the version to copy.**
