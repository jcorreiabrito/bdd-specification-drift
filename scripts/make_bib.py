#!/usr/bin/env python
"""Generate paper/refs.bib from the Crossref-verified reference table.

The bibliography is generated, never hand-written: every entry must trace to a row in
refs/verified.csv that scripts/audit_refs.py has confirmed against Crossref.

Three hard-won constraints, each of which broke the build at least once:

1. **Pure ASCII output.** BibTeX is an 8-bit program; `format.name$` and `change.case$`
   corrupt multi-byte UTF-8 and strip bare accent commands, producing .bbl files that
   pdfLaTeX rejects ("Invalid UTF-8 byte sequence") or that lose a backslash.
   Diacritics are therefore transliterated to their ASCII base letters.

2. **LaTeX markup from Crossref must be removed first.** Some venues (notably SBSI)
   return titles such as "Metodologias {\\'A}geis" or "Informa{\\c{c}}{\\~a}o".
   Passing that through the transliterator produced nested braces and an unbalanced
   .bib, which BibTeX rejected with "Illegal end of database file".

3. **Braces must balance.** The writer asserts this before writing, so a malformed
   bibliography fails here rather than deep inside the LaTeX build.

Usage:
    python scripts/make_bib.py
"""
from __future__ import annotations

import csv
import html
import os
import re
import sys
import unicodedata

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_IN = os.path.join(ROOT, "refs", "verified.csv")
BIB_OUT = os.path.join(ROOT, "paper", "refs.bib")

# LaTeX accent commands: \'A, \`a, \^o, \"u, \~n, \=a, \.z, \c{c}, \v{s}, \u{g}
ACCENT_RX = re.compile(r"\\['`\^\"~=.]\s*\{?(\w)\}?")
LETTER_ACCENT_RX = re.compile(r"\\[cvuHtbd]\s*\{(\w)\}")

PUNCT = {
    "\u2013": "--", "\u2014": "---", "\u2018": "`", "\u2019": "'",
    "\u201c": "``", "\u201d": "''", "\u2026": r"\ldots{}",
    "\u00d7": r"$\times$", "\u00b0": r"$^{\circ}$", "\u00b1": r"$\pm$",
    "\u00a0": " ",
}


def clean_latex(s: str) -> str:
    """Remove HTML entities and LaTeX accent markup, keeping the base letter."""
    s = html.unescape(s or "")
    s = LETTER_ACCENT_RX.sub(r"\1", s)   # \c{c} -> c, \v{s} -> s
    s = ACCENT_RX.sub(r"\1", s)          # \'A  -> A
    s = s.replace("\\", "").replace("{", "").replace("}", "")
    return s


def translit(s: str) -> str:
    """Pure-ASCII rendering: punctuation mapped, diacritics stripped."""
    out = []
    for ch in s or "":
        if ord(ch) < 128:
            out.append(ch)
        elif ch in PUNCT:
            out.append(PUNCT[ch])
        else:
            out.append("".join(c for c in unicodedata.normalize("NFKD", ch) if ord(c) < 128))
    return "".join(out)


def esc(s: str) -> str:
    """Escape for LaTeX text mode, after cleaning and transliterating."""
    s = translit(clean_latex(s))
    s = s.replace("&", r"\&").replace("%", r"\%").replace("#", r"\#").replace("_", r"\_")
    return re.sub(r"\s+", " ", s).strip()


def clean_title(s: str) -> str:
    """Escape title and strip stray Crossref footnote superscripts like 'Research1'."""
    s = esc(s)
    # Strip a single trailing footnote digit directly glued to a word (e.g., MISQ 'Impact1', 'Research1').
    s = re.sub(r"([A-Za-z]{4,})1$", r"\1", s)
    return s


def bib_author(a: str) -> str:
    """'Surname, I.; Surname, I.' -> 'Surname, I. and Surname, I.'"""
    a = translit(clean_latex(a)).replace('"', "")
    parts = [p.strip() for p in a.split(";") if p.strip()]
    if not parts:
        return "Anonymous"
    if parts[-1].lower().endswith("et al."):
        parts[-1] = parts[-1][:-len("et al.")].strip().rstrip(",;")
        return " and ".join(parts) + " and others"
    return " and ".join(parts)


def entry_type(venue: str) -> str:
    v = (venue or "").lower()
    if any(t in v for t in ("transactions", "journal", "quarterly", "review",
                            "letters", "mis quarterly", "systems journal")):
        return "article"
    if any(t in v for t in ("proceedings", "conference", "workshop", "symposium")):
        return "inproceedings"
    return "article"


def main() -> int:
    if not os.path.exists(CSV_IN):
        print(f"make_bib: missing {CSV_IN}")
        return 1
    with open(CSV_IN, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    entries: list[str] = []
    seen: set[str] = set()
    for r in rows:
        key = (r.get("key") or "").strip()
        if not key or key in seen:
            continue
        seen.add(key)
        etype = entry_type(r.get("venue", ""))
        fields = [("author", bib_author(r.get("authors", ""))),
                  ("title", clean_title(r.get("title", ""))),
                  ("year", (r.get("year") or "").strip())]
        venue = esc(r.get("venue", ""))
        if etype == "article":
            m = re.search(r"\s(\d+)\s*\((\d+)\)\s*$", r.get("venue", ""))
            fields.append(("journal", re.sub(r"\s*\d+\s*\(\d+\)\s*$", "", venue)))
            if m:
                fields.append(("volume", m.group(1)))
                fields.append(("number", m.group(2)))
        else:
            fields.append(("booktitle", venue))
        if (r.get("doi") or "").strip():
            fields.append(("doi", esc(r["doi"].strip())))
        if (r.get("source_url") or "").strip():
            fields.append(("url", esc(r["source_url"].strip())))

        body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields if v)
        entries.append(f"@{etype}{{{key},\n{body}\n}}\n")

    header = ("% GENERATED by scripts/make_bib.py from refs/verified.csv.\n"
              "% Every entry has a Crossref-resolved DOI (scripts/audit_refs.py).\n"
              "% Pure ASCII by design: BibTeX corrupts multi-byte characters.\n"
              "% Do not edit by hand; re-run the generator.\n\n")
    text = header + "\n".join(entries)

    # Fail here rather than inside the LaTeX build.
    if text.count("{") != text.count("}"):
        print(f"make_bib: FATAL unbalanced braces ({text.count('{')} vs {text.count('}')})")
        bad = [e for e in entries if e.count("{") != e.count("}")]
        for b in bad[:5]:
            print("  offending entry:", b.splitlines()[0])
        return 1
    if any(ord(c) > 127 for c in text):
        print("make_bib: FATAL non-ASCII content remains")
        return 1

    os.makedirs(os.path.dirname(BIB_OUT), exist_ok=True)
    with open(BIB_OUT, "w", encoding="ascii", newline="\n") as f:
        f.write(text)
    print(f"make_bib: wrote {len(entries)} entries -> {BIB_OUT} (ASCII, braces balanced)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
