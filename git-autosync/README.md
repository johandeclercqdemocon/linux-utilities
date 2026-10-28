# git-autosync

Commits and pushes new and edited files in `~/claude/my_recipes` and `~/claude/utilities`
to their private GitHub repos, so a recipe saved from ONLYOFFICE or Nautilus reaches GitHub
without anyone typing `git`.

## How it works

- `git-autosync REPO...` — for each repo: if there are changes and the newest one is at
  least `QUIET` seconds old (default 30, so autosaves in progress are left alone), it runs
  `git add -A`, commits as `Auto-sync: <files>`, and pushes `HEAD` to `origin`.
- A systemd **user timer** runs it every minute (`git-autosync.timer` → `git-autosync.service`,
  symlinked into `~/.config/systemd/user/`).
- Lock/temp files (`.~lock.*`, `~$*`, `*.swp`, `*.tmp`) are in each repo's `.gitignore`.
- **Secret guard:** if a changed file is named like `.env*`, `*.pem`, `*.key`, `*credentials*`,
  `*secret*` or `id_rsa*`, nothing is committed for that run and the file names are logged.
  This is a filename check only; it does not read file contents.

## Install

```bash
U=~/claude/utilities/git-autosync
mkdir -p ~/.config/systemd/user
ln -sf $U/git-autosync.service $U/git-autosync.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now git-autosync.timer
```

## Operate

```bash
systemctl --user list-timers git-autosync.timer      # next/last run
journalctl --user -u git-autosync.service -n 20      # what it pushed or refused
systemctl --user disable --now git-autosync.timer    # stop auto-pushing
```

## Notes

- Everything saved in those folders is pushed, including deletions. Don't put anything there
  you wouldn't want on GitHub (the repos are private, but still remote).
- Add another repo by appending its path to `ExecStart` in `git-autosync.service`.
- The timer runs only while you are logged in (user lingering is off), which is fine for
  a desktop.
- Does not pull: if a repo is also edited from another machine, a push can be rejected
  (visible in the journal) until you merge by hand.
