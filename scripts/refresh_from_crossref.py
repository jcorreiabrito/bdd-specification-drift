#!/usr/bin/env python
"""Re-derive bibliographic fields for every verified reference from Crossref.

Why this exists: an earlier PowerShell round-trip double-encoded refs/verified.csv,
irrecoverably corrupting non-ASCII characters in author names ("Guéhéneuc" became
"MÃ©hÃ©neuc" and then U+FFFD). Rather than guess at the original characters, we
re-fetch each DOI's Crossref record and overwrite `title`, `authors`, `year` and
`venue` with the authoritative values. Scout-supplied evidence fields
(`supporting_sentence`, `relevance`, `retrieval_date`, ...) are preserved untouched,
because those are human notes, not bibliographic data.

Usage:
    python scripts/refresh_from_crossref.py
"""
from __future__ import annotations

import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_IN = os.path.join(ROOT, "refs", "verified.csv")
CACHE = os.path.join(ROOT, "data", "raw", "crossref_cache.json")
UA = "bdd-specification-drift/1.0 (mailto:correiadebrito.joao@gmail.com)"
FIELDS = ["key", "title", "authors", "year", "venue", "doi", "retrieval_date",
          "source_url", "verified_via", "supporting_sentence", "relevance"]


def load_cache() -> dict:
    if os.path.exists(CACHE):
        try:
            return json.load(open(CACHE, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def fetch(doi: str, cache: dict) -> dict | None:
    d = doi.lower().strip()
    if d in cache and cache[d]:
        return cache[d]
    url = "https://api.crossref.org/works/" + urllib.parse.quote(d)
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=45) as r:
                msg = json.loads(r.read().decode("utf-8"))["message"]
            cache[d] = msg
            time.sleep(0.4)
            return msg
        except urllib.error.HTTPError as e:
            if e.code == 404:
                cache[d] = None
                return None
            time.sleep(1.5 * (attempt + 1))
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return None


def authors_of(msg: dict) -> str:
    out = []
    for a in msg.get("author", []) or []:
        fam = a.get("family") or a.get("name") or "?"
        giv = a.get("given", "")
        ini = "".join(p[0] + "." for p in giv.replace("-", " ").split() if p) if giv else ""
        out.append(f"{fam}, {ini}".strip().rstrip(","))
    if len(out) > 6:
        return "; ".join(out[:6]) + " et al."
    return "; ".join(out)


def year_of(msg: dict) -> str:
    for k in ("published-print", "published-online", "issued", "created"):
        dp = (msg.get(k) or {}).get("date-parts") or [[None]]
        if dp and dp[0] and dp[0][0]:
            return str(dp[0][0])
    return ""


def main() -> int:
    with open(CSV_IN, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    cache = load_cache()
    updated = failed = 0
    for r in rows:
        doi = (r.get("doi") or "").strip()
        if not doi:
            continue
        msg = fetch(doi, cache)
        if not msg:
            failed += 1
            print(f"  MISS {doi}")
            continue
        new_title = (msg.get("title") or [""])[0]
        new_auth = authors_of(msg)
        new_venue = (msg.get("container-title") or [""])[0] or msg.get("publisher", "")
        new_year = year_of(msg)
        changed = []
        if new_title and new_title != r.get("title"):
            r["title"] = new_title
            changed.append("title")
        if new_auth and new_auth != r.get("authors"):
            r["authors"] = new_auth
            changed.append("authors")
        if new_venue and new_venue != r.get("venue"):
            r["venue"] = new_venue
            changed.append("venue")
        # Keep an explicit issue-year only when Crossref disagrees by more than 1.
        if new_year and new_year != r.get("year"):
            try:
                if abs(int(new_year) - int(r.get("year") or "0")) > 1:
                    r["year"] = new_year
                    changed.append("year")
            except ValueError:
                r["year"] = new_year
                changed.append("year")
        if changed:
            updated += 1
            print(f"  {r['key']}: updated {','.join(changed)}")
    with open(CSV_IN, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    try:
        json.dump(cache, open(CACHE, "w", encoding="utf-8"))
    except Exception:
        pass
    print(f"refresh: {updated} row(s) updated, {failed} DOI(s) unresolved, {len(rows)} total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
