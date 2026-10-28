# nautilus-office-templates

Adds **New Document → Document / Spreadsheet / Presentation / PDF** to the right-click menu
in Nautilus (Ubuntu GNOME file manager), and opens the result in ONLYOFFICE.

## Files

| File | Creates |
|---|---|
| `New Document.docx` | blank Word-format document |
| `New Spreadsheet.xlsx` | blank spreadsheet |
| `New Presentation.pptx` | blank presentation |
| `New PDF.pdf` | blank one-page A4 PDF |

These are minimal hand-built OOXML files (zip of XML), not saved from an office suite.

## How it works

1. Nautilus lists every file in `~/Templates` under right-click → *New Document*.
   `~/Templates` holds **symlinks** to the files in this directory, so this directory is the source of truth.
2. ONLYOFFICE is the default app for the three Office MIME types, so a double-click opens it there.
   `application/pdf` is set to ONLYOFFICE too (previously Evince), so every PDF opens there. To revert:
   `xdg-mime default org.gnome.Evince.desktop application/pdf`.

## Install on a new machine

```bash
U=~/claude/utilities/nautilus-office-templates
mkdir -p ~/Templates
for f in "$U"/New*; do ln -sf "$f" ~/Templates/; done
D=onlyoffice-desktopeditors_onlyoffice-desktopeditors.desktop   # snap; adjust if installed differently
for m in application/pdf application/vnd.openxmlformats-officedocument.{wordprocessingml.document,spreadsheetml.sheet,presentationml.presentation}; do
  xdg-mime default $D $m
done
nautilus -q
```

## Notes

- Changing the default app also affects every existing `.docx/.xlsx/.pptx`, not only new files.
- Not yet verified that ONLYOFFICE opens the blank files; if one fails, replace it with a file saved from ONLYOFFICE.
- Needs ONLYOFFICE Desktop Editors (snap `onlyoffice-desktopeditors`).
