#!/usr/bin/env python
"""Canonical Crossref verifier for this project.

Two jobs:
  1. `search "<title>"`  -> candidate DOIs + metadata, so a scout can find the DOI
  2. `doi <doi>`         -> full metadata for one DOI, for the refs/verified.csv row

Deliberately strict: it reports what Crossref actually returned and never guesses.
Polite pool: set a contactable User-Agent, as Crossref asks.

Usage:
    python scripts/verify_ref.py search "Mutation testing in practice using Ruby"
    python scripts/verify_ref.py doi 10.1016/j.infsof.2020.106311
    python scripts/verify_ref.py search "..." --rows 5
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request

UA = "bdd-specification-drift/1.0 (mailto:correiadebrito.joao@gmail.com)"
BASE = "https://api.crossref.org/works"


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode("utf-8"))


def _authors(msg: dict) -> str:
    out = []
    for a in msg.get("author", []) or []:
        fam = a.get("family") or a.get("name") or "?"
        giv = a.get("given", "")
        ini = "".join(p[0] + "." for p in giv.replace("-", " ").split() if p) if giv else ""
        out.append(f"{fam}, {ini}".strip().rstrip(","))
    if len(out) > 6:
        return "; ".join(out[:6]) + " et al."
    return "; ".join(out)


def _year(msg: dict) -> str:
    for k in ("published-print", "published-online", "issued", "created"):
        parts = (msg.get(k) or {}).get("date-parts") or [[None]]
        if parts and parts[0] and parts[0][0]:
            return str(parts[0][0])
    return "NR"


def _venue(msg: dict) -> str:
    return (msg.get("container-title") or [""])[0] or msg.get("publisher", "") or "NR"


def do_doi(doi: str) -> int:
    doi = doi.replace("https://doi.org/", "").strip()
    msg = _get(f"{BASE}/{urllib.parse.quote(doi)}")["message"]
    rec = {
        "key": "",
        "title": (msg.get("title") or ["NR"])[0],
        "authors": _authors(msg),
        "year": _year(msg),
        "venue": _venue(msg),
        "doi": msg.get("DOI", doi),
        "type": msg.get("type", ""),
        "publisher": msg.get("publisher", ""),
        "url": msg.get("URL", f"https://doi.org/{doi}"),
    }
    print(json.dumps(rec, ensure_ascii=False, indent=2))
    return 0


def do_search(query: str, rows: int) -> int:
    url = f"{BASE}?query.bibliographic={urllib.parse.quote(query)}&rows={rows}&select=DOI,title,author,container-title,issued,type"
    items = _get(url)["message"]["items"]
    for i, msg in enumerate(items, 1):
        print(f"[{i}] {msg.get('DOI')}")
        print(f"    title  : {(msg.get('title') or ['NR'])[0][:150]}")
        print(f"    authors: {_authors(msg)}")
        print(f"    year   : {_year(msg)}   venue: {_venue(msg)}   type: {msg.get('type')}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["search", "doi"])
    ap.add_argument("query")
    ap.add_argument("--rows", type=int, default=3)
    a = ap.parse_args()
    return do_search(a.query, a.rows) if a.mode == "search" else do_doi(a.query)


if __name__ == "__main__":
    sys.exit(main())
