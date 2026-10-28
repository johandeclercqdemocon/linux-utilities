# doc-check

Checks a document for signs of AI writing and tells you what to change. It reads Markdown, plain text, HTML, Word (.docx), OpenDocument (.odt) and PDF.

The check has two parts:

1. **Mechanical check**, free and local. `voice_check.py` looks for forbidden words and phrases, dashes, uniform sentence and paragraph length, missing contractions, planted fragments, Title Case headings, bold labels, chatbot phrases and placeholders.
2. **Model review.** A Claude model reads the document against the same rules and reports what a script can't see: significance claims, invented or unsupported facts, vague attribution, hedging, aphorisms, negative parallelism in any form. Each finding comes with the exact quote, the rule ID, the problem and a rewrite. The tool then looks up every quote in the document and marks any it can't find.

## Files

| File | What it is |
|---|---|
| `scripts/doc_check.py` | The program: loads the document, runs both checks, writes the report |
| `scripts/voice_check.py` | The mechanical check; also works on its own (`python3 scripts/voice_check.py --help`) |
| `references/human-voice-rules.md` | The rules, with examples, and the forbidden-word list that `voice_check.py` reads |

Everything the tool needs is in this folder. Keep the three files in this layout: `voice_check.py` finds the rules at `../references/`.

## Requirements

- Python 3.10 or later.
- For `--backend subscription`: the Claude Code CLI (`claude`), logged in.
- For `--backend api`: an `ANTHROPIC_API_KEY` and the `anthropic` SDK. `uv run` installs the SDK from the script header.
- For PDF input: `pdftotext` (package `poppler-utils`).

## Usage

```bash
cd ~/claude/utilities/doc-check
python3 scripts/doc_check.py report.docx                     # model review on your subscription
uv run scripts/doc_check.py report.pdf --backend api         # model review on the API (billed)
python3 scripts/doc_check.py notes.md --backend none         # mechanical check only, free
python3 scripts/doc_check.py manual.md --mode ste --out review.md
```

## Where the model runs

| Backend | Runs on | Cost |
|---|---|---|
| `subscription` (default) | `claude -p` with your Claude login | No API billing. It counts against your plan's usage limits. |
| `api` | The Anthropic API with `ANTHROPIC_API_KEY` | Billed per token. The tool counts the tokens first (free), shows an estimate and asks before the first billed call. |
| `none` | Nothing | Free. Mechanical check only. |

On the subscription backend, the tool removes `ANTHROPIC_API_KEY` and `ANTHROPIC_AUTH_TOKEN` from the environment of `claude -p`. Without that, a set key would take priority over your login and the review would bill the API. It also runs with `--setting-sources ""` and no tools, so your hooks and settings don't fire inside the check.

On the API backend, the key comes from the environment, or from the `ANTHROPIC_API_KEY=` line in `~/.bashrc` if it isn't set. It goes only to the SDK client of that one process. The tool never puts it in the environment and never prints it; it prints the length and the first seven characters so you can see which key loaded. In a run without a terminal it won't bill unless you add `--yes`, and `--max-usd` stops it before the call if the estimate is higher.

## Options

| Option | Default | Meaning |
|---|---|---|
| `--backend` | `subscription` | `subscription`, `api` or `none` |
| `--mode` | `free` | `free` applies every rule. `ste` is for Simplified Technical English text, where contractions and fragments are wrong. |
| `--model` | `claude-opus-5-5` | Any Claude model ID |
| `--effort` | `medium` | `low`, `medium`, `high`, `xhigh` or `max` |
| `--allow` | | Comma-separated technical terms the word list should let through, for example `robust,landscape` |
| `--out` | stdout | Write the report to a file |
| `--json` | | JSON instead of Markdown |
| `--yes` | | API only: don't ask before the billed call |
| `--max-usd` | | API only: stop if the estimate is higher |

A document longer than 8,000 words is split at paragraph breaks, each part is reviewed, and the results are merged. The AI likelihood is the average of the parts, weighted by length.

Exit code 0 means no findings, 1 means findings, and 2 means the check couldn't run (missing file, no login, refused call, and so on).

## Measured on 2026-10-28

| Text | Backend | Mechanical errors | Model findings | AI likelihood | Cost |
|---|---|---|---|---|---|
| AI-style sample, 148 words | subscription | 24 | 10 | 99 | no API billing (31 s) |
| AI-style sample, 148 words | api, Opus 5.5 | 24 | 12, all quotes found | 98 | $0.0792 (estimate $0.067 to $0.14) |
| Human-written sample, 176 words | subscription | 0 | 0 | 12 | no API billing |

All five input formats gave the same mechanical result on the same text, and a 154,000-word PDF loads in one pass.

## Limits

- Neither check can tell whether a claim is true. Check facts and sources yourself.
- The model's AI likelihood is one reader's judgment, not a detector score. In the A/B tests behind the rules, the same judge scored the same texts up to 12 points apart on two runs.
- The rules flag human writing too: they are style rules, not proof of authorship.

## Source

The three files are copies from the simplified-technical-english skill in the private `claude-env` repo, where they are maintained. After changing them there, copy them here:

```bash
SK=~/claude-env/user/skills/simplified-technical-english
cp $SK/scripts/doc_check.py $SK/scripts/voice_check.py ~/claude/utilities/doc-check/scripts/
cp $SK/references/human-voice-rules.md ~/claude/utilities/doc-check/references/
```
