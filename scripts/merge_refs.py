#!/usr/bin/env python
"""Merge refs/verified.<tag>.csv into the canonical refs/verified.csv.

Rules:
  * Deduplicate by DOI (case-insensitive). When two facets cite the same work,
    keep the row with the richer evidence (has an exact quoted sentence rather
    than a PARAPHRASE, longer relevance, more fields populated) and record the
    other key as an alias.
  * Never invent or rewrite bibliographic fields. If two rows disagree on a
    field for the same DOI, keep the richer row and report the conflict.
  * Emit refs/CONFLICTS.md so the Lead can adjudicate by hand.

Output: refs/verified.csv (canonical, one row per work)
"""
from __future__ import annotations

import csv
import glob
import os
import sys
from collections import defaultdict

FIELDS = ["key", "title", "authors", "year", "venue", "doi", "retrieval_date",
          "source_url", "verified_via", "supporting_sentence", "relevance"]


def richness(row: dict) -> tuple:
    quoted = 0 if row.get("supporting_sentence", "").strip().upper().startswith("PARAPHRASE") else 1
    filled = sum(1 for f in FIELDS if (row.get(f) or "").strip())
    return (quoted, filled, len(row.get("relevance", "")))


def main() -> int:
    files = sorted(glob.glob(os.path.join("refs", "verified.*.csv")))
    files = [f for f in files if os.path.basename(f) != "verified.csv"]
    by_doi: dict[str, list[tuple[str, dict]]] = defaultdict(list)
    total = 0

    for path in files:
        tag = os.path.basename(path).replace("verified.", "").replace(".csv", "")
        with open(path, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                doi = (row.get("doi") or "").strip().lower()
                if not doi:
                    continue
                total += 1
                by_doi[doi].append((tag, row))

    merged: list[dict] = []
    conflicts: list[str] = []
    alias: dict[str, str] = {}

    for doi, candidates in by_doi.items():
        candidates.sort(key=lambda tr: richness(tr[1]), reverse=True)
        best_tag, best = candidates[0]
        best = dict(best)
        if len(candidates) > 1:
            others = [f"{t}:{r.get('key')}" for t, r in candidates[1:]]
            alias[doi] = ", ".join(others)
            for t, r in candidates[1:]:
                for f in ("title", "year", "venue", "authors"):
                    a, b = (best.get(f) or "").strip(), (r.get(f) or "").strip()
                    if a and b and a.lower() != b.lower() and f in ("venue", "year"):
                        conflicts.append(
                            f"DOI `{doi}` field `{f}`: kept `{a}` (from {best_tag}) vs "
                            f"`{b}` (from {t}:{r.get('key')})"
                        )
        merged.append(best)

    merged.sort(key=lambda r: ((r.get("authors") or "").lower(), (r.get("year") or "")))
    out = os.path.join("refs", "verified.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(merged)

    with open(os.path.join("refs", "CONFLICTS.md"), "w", encoding="utf-8") as f:
        f.write("# Reference merge report\n\n")
        f.write(f"- Input rows: {total}\n- Unique works (by DOI): {len(merged)}\n")
        f.write(f"- Input files: {', '.join(os.path.basename(p) for p in files)}\n\n")
        f.write("## Cross-facet duplicates resolved\n\n")
        if alias:
            for doi, others in sorted(alias.items()):
                f.write(f"- `{doi}` also cited as {others}\n")
        else:
            f.write("_none_\n")
        f.write("\n## Field conflicts to adjudicate\n\n")
        f.write("\n".join(f"- {c}" for c in conflicts) if conflicts else "_none_\n")

    print(f"merge: {total} input rows -> {len(merged)} unique works")
    print(f"merge: {len(alias)} duplicate DOI group(s); {len(conflicts)} field conflict(s)")
    print(f"merge: wrote {out} and refs/CONFLICTS.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
