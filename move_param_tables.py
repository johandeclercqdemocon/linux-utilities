"""Move each `#### name` block's parameter table into the chapter's `## Reference` section.

    python move_param_tables.py BOOK_ROOT "TEMPLATE"      # TEMPLATE has {name}, e.g. "The table under `{name}` ..."

At first use the block keeps its heading, its signature and its prose, and gains one sentence (TEMPLATE)
that says where the table is. In `## Reference`, after the index, a `### Parameters` part holds one
`##### `name`` heading and its table for each block, in the order the blocks appear. Five hashes, so a
checker that counts `#### ` blocks does not see a second block. Idempotent: a block with no table is left.
"""
from __future__ import annotations

import pathlib
import re
import sys

HEAD = re.compile(r"^#### `([A-Za-z_][\w.]*)`\s*$")
TABLE_START = re.compile(r"^\| parameter \| default \|")


def split_lines(text: str) -> list[str]:
    return text.splitlines(keepends=True)


def transform(text: str, template: str) -> tuple[str, int]:
    lines = split_lines(text)
    out, moved = [], []
    in_fence, current, i = False, None, 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence and re.match(r"#{1,6} ", line):
            m = HEAD.match(line.rstrip("\n"))
            current = m.group(1) if m else None
        if not in_fence and current and TABLE_START.match(line):
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            moved.append((current, "".join(lines[i:j])))
            out.append(template.format(name=current) + "\n")
            i = j
            continue
        out.append(line)
        i += 1
    if not moved:
        return text, 0
    text = "".join(out)
    part = "\n### Parameters\n\n" + "".join(f"##### `{n}`\n\n{tbl}\n" for n, tbl in moved)
    ref = re.search(r"^## Reference\n", text, re.M)
    if not ref:
        raise SystemExit("no ## Reference section")
    nxt = re.compile(r"^## ", re.M).search(text, ref.end())
    end = nxt.start() if nxt else len(text)
    body = text[ref.end():end].rstrip("\n") + "\n" + part
    return text[:ref.end()] + body + "\n" + text[end:], len(moved)


def main() -> None:
    root, template = pathlib.Path(sys.argv[1]), sys.argv[2]
    total = 0
    for p in sorted((root / "chapters").glob("*.md")):
        new, n = transform(p.read_text(encoding="utf-8"), template)
        if n:
            p.write_text(new, encoding="utf-8")
            print(f"{p.name}: {n} tables moved")
            total += n
    print(f"{total} tables moved")


if __name__ == "__main__":
    main()
