#!/usr/bin/env python
"""Generate paper/refs.bib from the Crossref-verified reference table.

The bibliography is generated, never hand-written: every entry in the manuscript
must trace to a row in refs/verified.csv that scripts/audit_refs.py has confirmed
against Crossref. Hand-edited .bib files are exactly how unverifiable references
creep into a paper.

The iSys class uses BibTeX with `apalike-sol.bst` (APA-based), so entries carry
author/title/year/journal-or-booktitle/volume/number/pages/doi/url as available.

Usage:
    python scripts/make_bib.py
"""
from __future__ import annotations

import csv
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_IN = os.path.join(ROOT, "refs", "verified.csv")
BIB_OUT = os.path.join(ROOT, "paper", "refs.bib")

TYPE_HINTS = [
    (re.compile(r"journal", re.I), "article"),
    (re.compile(r"transactions|journal|quarterly|review|letters", re.I), "article"),
]


def bib_author(a: str) -> str:
    """'Surname, I.; Surname, I.' -> 'Surname, I. and Surname, I.'"""
    a = translit((a or "").strip())
    # Scouts occasionally wrote LaTeX escapes into the CSV (e.g. B\"orstler); strip
    # them so the generated .bib cannot contain a stray backslash.
    a = a.replace("\\", "").replace("{", "").replace("}", "")
    if not a:
        return "Anonymous"
    parts = [p.strip() for p in re.split(r";", a) if p.strip()]
    if parts and parts[-1].lower().endswith("et al."):
        parts[-1] = parts[-1][:-len("et al.")].strip().rstrip(",;")
        joined = " and ".join(parts) + " and others"
    else:
        joined = " and ".join(parts)
    return joined.replace('"', "")


def esc(s: str) -> str:
    s = translit((s or "").strip())
    s = s.replace("\\", "")
    # Protect characters that break BibTeX/LaTeX.
    s = s.replace("&", "\\&").replace("%", "\\%").replace("#", "\\#")
    s = s.replace("_", "\\_")
    return re.sub(r"\s+", " ", s)


def entry_type(venue: str, title: str) -> str:
    v = venue or ""
    for rx, t in TYPE_HINTS:
        if rx.search(v):
            return t
    if re.search(r"proceedings|conference|workshop|symposium|international conference", v, re.I):
        return "inproceedings"
    if re.search(r"arxiv|preprint", v, re.I):
        return "misc"
    return "inproceedings" if re.search(r"conference|workshop|proceedings", v, re.I) else "article"


def esc_text(s: str) -> str:
    """Escape characters that are special in LaTeX text mode.

    DOIs and URLs routinely contain `_`, which LaTeX would treat as a subscript and
    abort with "! Missing $ inserted." (observed on 10.1007/978-3-030-49392-9_6).
    """
    s = (s or "").strip()
    s = s.replace("\\", "")
    s = s.replace("&", "\\&").replace("%", "\\%").replace("#", "\\#")
    s = s.replace("_", "\\_")
    return s


# BibTeX is an 8-bit program: its change.case$ / format.name$ functions corrupt or
# strip multi-byte UTF-8 and bare accent commands, producing .bbl files that pdfLaTeX
# rejects ("Invalid UTF-8 byte sequence") or that lose a backslash ("B\orstler").
# We therefore emit pure-ASCII .bib files and transliterate accented Latin letters to
# their unaccented ASCII base form. This is standard bibliographic practice and is
# lossless for search and citation purposes.
import unicodedata

PUNCT = {
    "\u2013": "--", "\u2014": "---", "\u2018": "`", "\u2019": "'",
    "\u201c": "``", "\u201d": "''", "\u2026": "\\ldots{}",
    "\u00d7": "$\\times$", "\u00b0": "$^{\\circ}$", "\u00b1": "$\\pm$",
    "\u00a0": " ",
}


def translit(s: str) -> str:
    out = []
    for ch in s or "":
        if ord(ch) < 128:
            out.append(ch)
            continue
        if ch in PUNCT:
            out.append(PUNCT[ch])
            continue
        base = "".join(c for c in unicodedata.normalize("NFKD", ch) if ord(c) < 128)
        out.append(base)
    return "".join(out)


def esc_text(s: str) -> str:
    """Escape characters that are special in LaTeX text mode.

    DOIs and URLs routinely contain `_`, which LaTeX would treat as a subscript and
    abort with "! Missing $ inserted." (observed on 10.1007/978-3-030-49392-9_6).
    """
    s = (s or "").strip()
    s = s.replace("\\", "")
    s = s.replace("&", "\\&").replace("%", "\\%").replace("#", "\\#")
    s = s.replace("_", "\\_")
    return s


# BibTeX is an 8-bit program and its change.case$ / format.name$ functions corrupt
# multi-byte UTF-8, producing ".bbl" files that pdfLaTeX rejects with
# "! LaTeX Error: Invalid UTF-8 byte sequence". The robust fix is to write pure-ASCII
# .bib files, transliterating accented Latin characters to LaTeX escapes.
TRANSLIT = {
    "á": "{\\'a", "à": "\\`a", "â": "\\^a", "ã": "\\~a", "ä": '\\"a', "å": "\\r{a}}",
    "Á": "{\\'A", "À": "\\`A", "Â": "\\^A", "Ã": "\\~A", "Ä": '\\"A', "Å": "\\r{A}}",
    "ó": "{\\'o", "ò": "\\`o", "ô": "\\^o", "õ": "\\~o", "ö": '\\"o', "ø": "\\o{}}",
    "Ó": "{\\'O", "Ò": "\\`O", "Ô": "\\^O", "Õ": "\\~O", "Ö": '\\"O', "Ø": "\\O{}}",
    "ç": "{\\c{c}", "Ç": "\\c{C}", "ñ": "\\~n", "Ñ": "\\~N}",
    "ć": "{\\'c", "Ć": "\\'C", "ń": "\\'n", "Ń": "\\'N", "ś": "\\'s", "Ś": "\\'S}",
    "ź": "{\\'z", "Ź": "\\'Z", "ż": "\\.z", "Ż": "\\.Z", "ł": "\\l{}", "Ł": "\\L{}}",
    "š": "{\\v{s}", "Š": "\\v{S}", "č": "\\v{c}", "Č": "\\v{C}", "ř": "\\v{r}}",
    "ž": "{\\v{z}", "Ž": "\\v{Z}", "ğ": "\\u{g}", "Ğ": "\\u{G}", "ı": "\\i{}}",
    "–": "--", "—": "---", "‘": "`", "’": "'", "“": "``", "”": "''",
    "…": "{\\ldots{}", "×": "$\\times$", "°": "$^{\\circ}$", "±": "$\\pm$}",
}


def translit(s: str) -> str:
    out = []
    for ch in s or "":
        if ord(ch) < 128:
            out.append(ch)
        else:
            out.append(TRANSLIT.get(ch, ""))
    return "".join(out)


def esc_text(s: str) -> str:
    """Escape characters that are special in LaTeX text mode.

    DOIs and URLs routinely contain `_`, which LaTeX would treat as a subscript and
    abort with "! Missing $ inserted." (observed on 10.1007/978-3-030-49392-9_6).
    Also transliterates to ASCII so BibTeX cannot corrupt multi-byte characters.
    """
    s = translit((s or "").strip())
    s = s.replace("\\", "")
    s = s.replace("&", "\\&").replace("%", "\\%").replace("#", "\\#")
    s = s.replace("_", "\\_")
    return s


def main() -> int:
    if not os.path.exists(CSV_IN):
        print(f"make_bib: missing {CSV_IN}")
        return 1
    with open(CSV_IN, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    os.makedirs(os.path.dirname(BIB_OUT), exist_ok=True)
    seen = set()
    out = [
        "% Generated by scripts/make_bib.py from refs/verified.csv.",
        "% Every entry has a Crossref-resolved DOI (see scripts/audit_refs.py).",
        "% Do not edit by hand: re-run the generator instead.",
        "",
    ]
    kept = 0
    for r in rows:
        key = (r.get("key") or "").strip()
        if not key or key in seen:
            continue
        seen.add(key)
        etype = entry_type(r.get("venue", ""), r.get("title", ""))
        fields = [
            ("author", bib_author(r.get("authors", ""))),
            ("title", esc(r.get("title", ""))),
            ("year", (r.get("year") or "").strip()),
        ]
        venue = esc(r.get("venue", ""))
        if etype == "article":
            # Recover volume/number from a venue string like "IEEE TSE 48(10)".
            m = re.search(r"(\d+)\s*\((\d+)\)\s*$", r.get("venue", ""))
            fields.append(("journal", re.sub(r"\s*\d+\s*\(\d+\)\s*$", "", venue)))
            if m:
                fields.append(("volume", m.group(1)))
                fields.append(("number", m.group(2)))
        elif etype == "inproceedings":
            fields.append(("booktitle", venue))
        else:
            fields.append(("howpublished", venue))
        if (r.get("doi") or "").strip():
            fields.append(("doi", esc_text(r["doi"].strip())))
        if (r.get("source_url") or "").strip():
            fields.append(("url", esc_text(r["source_url"].strip())))

        body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields if v)
        out.append(f"@{etype}{{{key},\n{body}\n}}\n")
        kept += 1

    with open(BIB_OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"make_bib: wrote {kept} entries -> {BIB_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
