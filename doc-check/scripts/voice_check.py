#!/usr/bin/env python3
"""voice_check.py - a check tool for the human-voice rules.

This tool finds signs of AI writing in text or Markdown. The rules and
their IDs are in references/human-voice-rules.md. The tool reads the
forbidden strings from section 9 of that file.
It uses only the Python standard library.

Usage:
    python3 voice_check.py [--mode free|ste] [--allow WORD,...] FILE...
    cat draft.txt | python3 voice_check.py --mode free

Mode "free" applies all the rules. Mode "ste" does not apply the rule
for contractions (V2) or the placement rules for fragments, because STE
does not permit contractions or fragments.

The tool ignores code blocks, inline code, URLs, block quotes, quoted
text, and YAML frontmatter.
Exit code 0 = no errors. Exit code 1 = one or more errors.
"""

import argparse
import re
import statistics
import sys
from pathlib import Path

# ---------------------------------------------------------------- constants

RULES_FILE = Path(__file__).resolve().parent.parent / "references" / "human-voice-rules.md"

# V1: minimum burstiness (stdev / mean of sentence length x 100) for each mode.
MIN_BURSTINESS = {"free": 35, "ste": 25}
FRAGMENT = 4                 # V3: a sentence of this many words or fewer
MIN_PAR_CV = 0.15            # V4: coefficient of variation of paragraph lengths

CONTRACTION = re.compile(
    r"\b\w+n't\b|\b\w+'(?:re|ll|ve|m|d)\b|"
    r"\b(?:it|that|there|what|let|who|here|he|she|where)'s\b",
    re.IGNORECASE,
)
DASH = re.compile(r"[—–]|(?<=\w) -- (?=\w)|(?<=\w)--(?=\w)")
CURLY = re.compile(r"[“”‘’]")
SYMBOL = re.compile(r"[←-⇿⟰-⟿✓-✘•]")
EMOJI = re.compile(r"[\U0001f300-\U0001faff☀-⛿✀-➿]")
BOLD = re.compile(r"\*\*[^*\n]+\*\*|__[^_\n]+__")
BOLD_LABEL = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+(?:\*\*[^*]+\*\*\s*:|\*\*[^*]+:\*\*)")
BULLET = re.compile(r"^\s*(?:[-*+]|\d+\.)\s")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])")
WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'&/-]*")
TRIAD = re.compile(r"\b[\w-]+(?: [\w-]+)?, [\w-]+(?: [\w-]+)?,? (?:and|or) [\w-]+\b")
SMALL_WORDS = {"a", "an", "the", "and", "or", "but", "of", "in", "on", "to", "for",
               "with", "at", "by", "from", "vs", "as", "is", "into", "per"}
SAFE_BOLD = {"warning", "caution", "note"}
# V3: fragment types that read as planted
LABEL_FRAGMENT = re.compile(r"^[A-Z][\w ]{0,20}: \S")
NUMBER_ECHO = re.compile(r"\b(?:than|half|twice|double|triple|third|quarter|percent)\b|%", re.I)
# S8: an email sign-off is not a dramatic closer
VALEDICTION = re.compile(r"^(?:thanks|thank you|best|cheers|regards|best regards|kind regards)\b[^.!?]{0,30}[.!,]?$", re.I)
TIME_FRAGMENT = re.compile(r"\b\d{1,2}:\d{2}\b|\b(?:mon|tues|wednes|thurs|fri|satur|sun)day\b", re.I)


# ---------------------------------------------------------------- helpers

def load_forbidden(path):
    """Read section 9 of the rules file. Return a list of (rule, regex)."""
    text = Path(path).read_text(encoding="utf-8")
    m = re.search(r"<!-- forbidden:start -->(.*?)<!-- forbidden:end -->", text, re.DOTALL)
    if not m:
        sys.exit(f"voice_check: no forbidden list in {path}")
    patterns = []
    for line in m.group(1).splitlines():
        line = line.strip()
        r = re.match(r"^([A-Z]\d+) re: (.+)$", line)
        if r:
            patterns.append((r.group(1), re.compile(r.group(2), re.IGNORECASE)))
            continue
        r = re.match(r"^([A-Z]\d+): (.+)$", line)
        if r:
            for phrase in r.group(2).split(", "):
                phrase = phrase.strip()
                rx = r"(?<![\w-])" + re.escape(phrase) + (r"(?![\w-])" if phrase[-1].isalnum() else "")
                patterns.append((r.group(1), re.compile(rx, re.IGNORECASE)))
    return patterns


def blank_keep_lines(m):
    return "\n" * m.group(0).count("\n")


def strip_markdown(text):
    """Remove the parts of the text that the rules do not control.

    The line count does not change, so the line numbers stay correct.
    """
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\A---\n.*?\n---\n", blank_keep_lines, text, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", blank_keep_lines, text, flags=re.DOTALL)
    text = re.sub(r"^```.*?^```[^\n]*$", blank_keep_lines, text, flags=re.DOTALL | re.MULTILINE)
    text = re.sub(r"`[^`\n]+`", " CODE ", text)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"https?://\S+", " URL ", text)
    text = re.sub(r"^>.*$", "", text, flags=re.MULTILINE)
    return text


def unquote(text):
    """Replace quoted text with one token. Quoted text is not controlled."""
    return re.sub(r"\"[^\"\n]*\"|“[^”\n]*”", " QUOTED ", text)


def words(s):
    return len(WORD.findall(s))


def sentences(par):
    return [s.strip() for s in SENT_SPLIT.split(par) if s.strip() and WORD.search(s)]


def blocks(lines):
    """Divide the lines into blocks. Return (kind, start_line, lines).

    kind is "heading", "table", "list", or "prose".
    """
    out, cur, kind, start = [], [], None, 0
    def flush():
        if cur:
            out.append((kind, start, list(cur)))
            cur.clear()
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not s:
            flush(); kind = None
            continue
        k = ("heading" if HEADING.match(s) else "table" if s.startswith("|")
             else "list" if BULLET.match(line) or (kind == "list" and line.startswith(" "))
             else "prose")
        if k == "heading" or k != kind:
            flush(); kind, start = k, i
        cur.append(line)
    flush()
    return out


# ---------------------------------------------------------------- checks

class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def error(self, line, rule, msg):
        self.errors.append((line, rule, msg))

    def warn(self, line, rule, msg):
        self.warnings.append((line, rule, msg))


def short(s, n=60):
    s = " ".join(s.split())
    return s if len(s) <= n else s[:n - 3] + "..."


def check_characters(raw_lines, report):
    """F1, F2, F6, F11, V5 dashes: checks on the text before unquote()."""
    for i, line in enumerate(raw_lines, 1):
        if DASH.search(line):
            report.error(i, "V5", f"dash: \"{short(line)}\". Use a comma, a colon, parentheses, or a new sentence.")
        if CURLY.search(line):
            report.error(i, "F1", "curly quote or apostrophe. Use straight quotes.")
        m = SYMBOL.search(line)
        if m:
            report.error(i, "F2", f"symbol \"{m.group(0)}\". Use a word.")
        m = EMOJI.search(line)
        if m:
            report.error(i, "F6", f"emoji \"{m.group(0)}\".")


def check_artifacts(original_lines, report):
    """F11, F12: tool artifacts and placeholders, also inside URLs."""
    art = re.compile(r"oaicite|contentReference|utm_source=|<mark>|↩|continue generating", re.I)
    ph = re.compile(r"\[(?:insert|describe|your|add|name|company|date)\b[^\]]*\]|\b\d{4}-XX-XX\b|\bYour Name\b", re.I)
    for i, line in enumerate(original_lines, 1):
        m = art.search(line)
        if m:
            report.error(i, "F11", f"tool artifact \"{m.group(0)}\".")
        m = ph.search(line)
        if m:
            report.error(i, "F12", f"placeholder \"{m.group(0)}\".")


def check_forbidden(lines, patterns, allow, report):
    for i, line in enumerate(lines, 1):
        norm = line.replace("’", "'")
        for rule, rx in patterns:
            for m in rx.finditer(norm):
                hit = m.group(0).strip(" ,.")
                if hit.lower() in allow:
                    continue
                report.error(i, rule, f"\"{hit}\" in \"{short(line)}\".")


def heading_level(line):
    m = HEADING.match(line.strip())
    return (len(m.group(1)), m.group(2).strip()) if m else (0, line.strip())


def check_headings(bl, allow, report):
    """F5, F7, F10."""
    last = 0
    for idx, (kind, start, lines) in enumerate(bl):
        if kind != "heading":
            continue
        level, text = heading_level(lines[0])
        if last and level > last + 1:
            report.error(start, "F10", f"heading level {level} after level {last}.")
        last = level
        ws = [w for w in re.findall(r"[A-Za-z][\w'-]*", text)]
        sig = [w for w in ws[1:] if w.lower() not in SMALL_WORDS and not w.isupper()]
        if len(sig) >= 2 and all(w[0].isupper() for w in sig) and text.lower() not in allow:
            report.error(start, "F5", f"Title Case heading \"{text}\". Use sentence case.")
        if re.match(r"^(?:\d+\.\s*)?(?:Why|What|Where)\b", text):
            report.error(start, "F7", f"question-word heading \"{text}\".")
        nxt = bl[idx + 1] if idx + 1 < len(bl) else None
        if nxt is None or nxt[0] == "heading" and heading_level(nxt[2][0])[0] > level:
            report.warn(start, "F10", f"heading \"{text}\" has no text under it.")


def check_lists_tables(bl, report):
    """F4, F8."""
    for kind, start, lines in bl:
        if kind == "list":
            for j, line in enumerate(lines):
                if BOLD_LABEL.match(line):
                    report.error(start + j, "F4", f"list item starts with a bold label: \"{short(line)}\".")
        elif kind == "table":
            rows = [l for l in lines if not re.match(r"^\|[\s:|-]+\|?$", l.strip())]
            if len(rows) - 1 < 3:
                report.warn(start, "F8", f"table has {len(rows) - 1} data rows. Put a small set in a sentence.")


def check_prose(bl, mode, report):
    """V1-V5, F3, S4, S5, S7, S8, S10, T5, W12 on the prose paragraphs."""
    pars = []                                  # (start_line, [sentences])
    for kind, start, lines in bl:
        if kind != "prose":
            continue
        par = " ".join(l.strip() for l in lines)
        for m in BOLD.finditer(par):
            if m.group(0).strip("*_").strip(":").lower() not in SAFE_BOLD:
                report.error(start, "F3", f"bold in prose: \"{m.group(0)}\".")
        par = unquote(par)
        sents = sentences(par)
        if sents:
            pars.append((start, sents))

    all_sents = [s for _, ss in pars for s in ss]
    lengths = [words(s) for s in all_sents]
    total = sum(lengths)

    # V1: burstiness over the full text, and short + long in each paragraph
    if len(lengths) >= 5:
        b = statistics.pstdev(lengths) / statistics.mean(lengths) * 100
        if b < MIN_BURSTINESS[mode]:
            report.error(0, "V1", f"burstiness is {b:.0f} (minimum {MIN_BURSTINESS[mode]}). "
                                  f"Sentence lengths: {lengths}.")

    # V4: paragraph lengths must not be almost equal
    plens = [sum(words(s) for s in ss) for _, ss in pars]
    if len(plens) >= 4:
        cv = statistics.pstdev(plens) / statistics.mean(plens)
        if cv < MIN_PAR_CV:
            report.error(0, "V4", f"paragraph lengths are almost equal {plens} "
                                  f"(variation {cv:.2f}, minimum {MIN_PAR_CV}).")

    # V5: punctuation variety in long free text
    prose_text = " ".join(all_sents)
    if mode == "free" and total >= 300 and not re.search(r"[:;()?]", prose_text):
        report.error(0, "V5", "only commas and periods in 300+ words. Use a colon, "
                              "parentheses, or a question where the meaning needs one.")

    # V2: contractions in free text
    if mode == "free" and total >= 100:
        n = len(CONTRACTION.findall(prose_text.replace("’", "'")))
        if n * 100 < total:
            report.error(0, "V2", f"{n} contractions in {total} words (minimum 1 in each 100).")

    # W12: "thus" one time at most
    n_thus = len(re.findall(r"\bthus\b", prose_text, re.I))
    if n_thus > 1:
        report.error(0, "W12", f"\"thus\" {n_thus} times (one time at most).")

    # V3: fragments are permitted, but not the planted types
    for start, ss in pars:
        for s in ss:
            if words(s) > FRAGMENT + 1:
                continue
            if LABEL_FRAGMENT.match(s):
                report.error(start, "V3", f"label fragment \"{s}\". Write a full sentence.")
            elif words(s) <= FRAGMENT and NUMBER_ECHO.search(s):
                report.error(start, "V3", f"number-echo fragment \"{s}\". Remove it.")
            elif words(s) <= FRAGMENT and TIME_FRAGMENT.search(s):
                report.error(start, "V3", f"time fragment \"{s}\". Join it to its sentence.")

    # S8 and V3: fragment placement
    if mode == "free":
        closers = [s for s in all_sents if not VALEDICTION.match(s)]
        if closers and words(closers[-1]) <= FRAGMENT and len(closers) > 3:
            report.warn(0, "S8", f"the text ends on a fragment: \"{closers[-1]}\".")
        for start, ss in pars:
            ls = [words(s) for s in ss]
            if sum(1 for l in ls if l <= FRAGMENT) > 1:
                report.error(start, "V3", f"more than one fragment in a paragraph: lengths {ls}.")

    for start, ss in pars:
        ls = [words(s) for s in ss]
        for a in range(len(ss) - 1):
            # S8: two fragments in sequence
            if ls[a] <= 3 and ls[a + 1] <= 3:
                report.error(start, "S8", f"fragments in sequence: \"{ss[a]} {ss[a + 1]}\".")
            # S7: short rhetorical question with a short answer
            if ss[a].endswith("?") and ls[a] <= 5 and ls[a + 1] <= FRAGMENT:
                report.error(start, "S7", f"rhetorical question and answer: \"{ss[a]} {ss[a + 1]}\".")
            # S4: negation chain
            if a + 1 < len(ss) and ss[a].startswith("Not ") and ss[a + 1].startswith("Not "):
                report.error(start, "S4", f"negation chain: \"{short(ss[a] + ' ' + ss[a + 1])}\".")
        # S10: three sentences in sequence with the same first word
        firsts = [WORD.findall(s)[0].lower() if WORD.findall(s) else "" for s in ss]
        for a in range(len(firsts) - 2):
            if mode == "ste" and firsts[a] in ("the", "a", "an"):
                continue
            if firsts[a] and firsts[a] == firsts[a + 1] == firsts[a + 2]:
                report.error(start, "S10", f"three sentences in sequence start with \"{firsts[a]}\".")
                break
        # S5: more than one list of three in a paragraph
        triads = TRIAD.findall(" ".join(ss))
        if len(triads) > 1:
            report.error(start, "S5", f"{len(triads)} lists of three in one paragraph: {triads}.")
        # T5: enumeration in prose
        if re.search(r"\bThe first\b.*\bThe second\b", " ".join(ss)):
            report.error(start, "T5", "\"The first ..., The second ...\" in prose. Use a list.")
    return total, lengths


def check_text(text, mode, patterns, allow, report):
    original = text.replace("\r\n", "\n").split("\n")
    stripped = strip_markdown(text)
    lines = stripped.split("\n")
    check_artifacts([unquote(l) for l in original], report)
    check_characters([unquote(l) for l in lines], report)
    check_forbidden([unquote(l) for l in lines], patterns, allow, report)
    bl = blocks(lines)
    check_headings(bl, allow, report)
    check_lists_tables(bl, report)
    return check_prose(bl, mode, report)


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="Check text against the human-voice rules.")
    ap.add_argument("files", nargs="*", help="files to check (default: stdin)")
    ap.add_argument("--mode", choices=["free", "ste"], default="free",
                    help="free: all rules. ste: no contraction or fragment rules (default: free)")
    ap.add_argument("--allow", default="",
                    help="comma-separated technical names to permit, for example robust,landscape. "
                         "A Title Case heading that is an official name is also permitted.")
    ap.add_argument("--rules", default=str(RULES_FILE), help="path to human-voice-rules.md")
    args = ap.parse_args()

    patterns = load_forbidden(args.rules)
    allow = {a.strip().lower() for a in args.allow.split(",") if a.strip()}
    sources = [(f, Path(f).read_text(encoding="utf-8")) for f in args.files] or [("stdin", sys.stdin.read())]

    n_err = 0
    for name, text in sources:
        report = Report()
        total, lengths = check_text(text, args.mode, patterns, allow, report)
        for line, rule, msg in sorted(report.errors):
            print(f"ERROR   {name}:{line or '-'} [{rule}] {msg}")
        for line, rule, msg in sorted(report.warnings):
            print(f"WARNING {name}:{line or '-'} [{rule}] {msg}")
        b = (statistics.pstdev(lengths) / statistics.mean(lengths) * 100) if len(lengths) >= 2 else 0
        print(f"{name}: {total} prose words, {len(lengths)} sentences, burstiness {b:.0f}. "
              f"{len(report.errors)} errors, {len(report.warnings)} warnings.")
        n_err += len(report.errors)

    if not n_err:
        print("The text obeys the human-voice rules that this tool can check.")
        print("The tool cannot check meaning: claims, sources, and the C rules need a manual check.")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
