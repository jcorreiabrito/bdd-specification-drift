#!/usr/bin/env python
"""Audit refs/verified.*.csv against Crossref.

Enforces the project's integrity rule: every citation must have a DOI that
Crossref actually resolves, and the Crossref title must match the title the
scout recorded. A scout can mistype a DOI or transpose two papers; this catches
that before a reference reaches the manuscript.

Checks per row:
  1. DOI resolves at api.crossref.org
  2. title similarity (normalised token overlap) above threshold
  3. year agrees (+-1 year tolerance, because print/online years differ)
  4. required fields present and non-empty
  5. duplicate DOIs / duplicate keys across files

Exit code 0 only if every row passes; otherwise 1.

Usage:
    python scripts/audit_refs.py            # audit all refs/verified.*.csv
    python scripts/audit_refs.py --fix-report out.md
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher

UA = "bdd-specification-drift/1.0 (mailto:correiadebrito.joao@gmail.com)"
REQUIRED = ["key", "title", "authors", "year", "venue", "doi", "retrieval_date",
            "source_url", "verified_via", "supporting_sentence", "relevance"]
CACHE = os.path.join("data", "raw", "crossref_cache.json")


def norm(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def load_cache() -> dict:
    if os.path.exists(CACHE):
        try:
            with open(CACHE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cache(c: dict) -> None:
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(c, f)


def crossref(doi: str, cache: dict) -> dict | None:
    doi = doi.replace("https://doi.org/", "").strip()
    if doi in cache:
        return cache[doi]
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=45) as r:
                msg = json.loads(r.read().decode("utf-8"))["message"]
            cache[doi] = msg
            time.sleep(0.35)
            return msg
        except urllib.error.HTTPError as e:
            if e.code == 404:
                cache[doi] = None
                return None
            time.sleep(1.5 * (attempt + 1))
        except Exception:  # noqa: BLE001 - 10054 resets are routine on this host
            time.sleep(1.5 * (attempt + 1))
    return cache.get(doi)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix-report", default=None)
    a = ap.parse_args()

    canonical = os.path.join("refs", "verified.csv")
    if os.path.exists(canonical):
        # Once the facets have been merged, the canonical file is the artefact that
        # feeds the bibliography; duplicate DOIs across facets are expected and are
        # resolved by scripts/merge_refs.py, so auditing the facets would report
        # false problems.
        files = [canonical]
    else:
        files = sorted(glob.glob(os.path.join("refs", "verified.*.csv")))
    if not files:
        print("audit: no refs/verified.*.csv found")
        return 1

    cache = load_cache()
    seen_dois: dict[str, str] = {}
    seen_keys: dict[str, str] = {}
    problems: list[str] = []
    ok = 0
    total = 0

    for path in files:
        tag = os.path.basename(path).replace("verified.", "").replace(".csv", "")
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            print(f"[{tag}] empty (header only)")
            continue
        for i, row in enumerate(rows, 2):
            total += 1
            where = f"{tag}:{i} key={row.get('key','?')}"
            missing = [c for c in REQUIRED if not (row.get(c) or "").strip()]
            if missing:
                problems.append(f"{where}: missing fields {missing}")
            doi = (row.get("doi") or "").strip()
            if not doi:
                problems.append(f"{where}: no DOI")
                continue
            key = (row.get("key") or "").strip()
            if doi.lower() in seen_dois:
                problems.append(f"{where}: duplicate DOI (also {seen_dois[doi.lower()]})")
            seen_dois[doi.lower()] = where
            if key in seen_keys:
                problems.append(f"{where}: duplicate key (also {seen_keys[key]})")
            seen_keys[key] = where

            msg = crossref(doi, cache)
            if msg is None:
                problems.append(f"{where}: DOI does not resolve at Crossref: {doi}")
                continue
            cr_title = (msg.get("title") or [""])[0]
            sim = SequenceMatcher(None, norm(row.get("title", "")), norm(cr_title)).ratio()
            if sim < 0.80:
                problems.append(
                    f"{where}: title mismatch (sim={sim:.2f}) recorded='{row.get('title','')[:70]}' "
                    f"crossref='{cr_title[:70]}'"
                )
                continue
            cr_year = None
            for k in ("published-print", "published-online", "issued"):
                dp = (msg.get(k) or {}).get("date-parts") or [[None]]
                if dp and dp[0] and dp[0][0]:
                    cr_year = int(dp[0][0])
                    break
            try:
                rec_year = int((row.get("year") or "0").strip())
            except ValueError:
                rec_year = 0
            if cr_year and rec_year and abs(cr_year - rec_year) > 1:
                problems.append(f"{where}: year mismatch recorded={rec_year} crossref={cr_year}")
                continue
            ok += 1

    save_cache(cache)
    print(f"\naudit: {ok}/{total} rows fully verified against Crossref.")
    if problems:
        print(f"audit: {len(problems)} problem(s):")
        for p in problems:
            print("  - " + p)
        if a.fix_report:
            with open(a.fix_report, "w", encoding="utf-8") as f:
                f.write("# Reference audit problems\n\n")
                for p in problems:
                    f.write(f"- {p}\n")
        return 1
    print("audit: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
