# utilities

Small machine helpers. Each utility lives in its own directory with its own README.

- [nautilus-office-templates](nautilus-office-templates/README.md) — right-click "New Document" in Nautilus, opening in ONLYOFFICE
- [git-autosync](git-autosync/README.md) — timer that commits and pushes my_recipes and utilities automatically
- [vscode-python-debugging](vscode-python-debugging/README.md) — makes F5 in VS Code run the open file as a module, not as a script
- [wifi-mesh-roaming](wifi-mesh-roaming/README.md) — fixes Teams dropouts from Wi-Fi switching between Deco mesh units; check script + undo
- [ollama-gpu-watchdog](ollama-gpu-watchdog/README.md) — shows when Ollama has loaded a model partly on the CPU (about 1.8× slower), and unloads it so it reloads fully onto the GPU
- [gvisor-docker](gvisor-docker/README.md) — installs gVisor as an extra Docker runtime (`runsc`), so that `bwrap` and `unshare -rn` work inside containers; check script, undo
- [doc-check](doc-check/README.md) — checks any document (.md, .docx, .pdf, .html, ...) for signs of AI writing: the free mechanical rules, then a Claude review on the subscription or the API; self-contained (rules and checker included)
- [move_param_tables.py](move_param_tables.py) — moves each `#### name` block's parameter table into the chapter's `## Reference` section, in the programming books (`python move_param_tables.py BOOK_ROOT "TEMPLATE"`)
- [skills](https://github.com/johandeclercqdemocon/claude-skills) — Claude Code skills picked from mattpocock/skills (MIT); its own public repo, cloned into `skills/` and ignored here

License: MIT, see [LICENSE](LICENSE).
