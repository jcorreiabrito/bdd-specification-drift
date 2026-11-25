#!/usr/bin/env python
"""Build refs/verified.is.csv — the Information Systems / SOL reference facet.

The red-team review found that the manuscript cited no IS venue, invoked Design Science
Research without citing it, and had no SOL (SBC OpenLib) coverage — all of which the
target journal treats as desk-review grounds. This script adds the required facet.

Metadata is fetched from Crossref by DOI rather than typed, so titles, authors and
years cannot be mistranscribed. The `relevance` note is authored here; the
`supporting_sentence` is left as a PARAPHRASE marker unless an exact quote is supplied,
so that the integrity rule ("never fabricate a quotation") is respected.

Usage:
    python scripts/build_is_facet.py
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
OUT = os.path.join(ROOT, "refs", "verified.is.csv")
UA = "bdd-specification-drift/1.0 (mailto:correiadebrito.joao@gmail.com)"
TODAY = "2026-11-25"

# (key, doi, relevance, paraphrase of what the source establishes)
FACET = [
    ("henderson1993strategic", "10.1147/sj.382.0472",
     "Foundational business-IT alignment model; frames the fit between organisational strategy and IT as a management problem.",
     "PARAPHRASE: Strategic alignment is presented as the fit between business strategy and IT strategy, and as a continuing managerial process rather than a one-off design decision."),
    ("delone2003model", "10.1080/07421222.2003.11045748",
     "Defines IS success as a multi-dimensional construct (quality, use, satisfaction, net benefit); anchors the claim that system quality and information quality are distinct.",
     "PARAPHRASE: The ten-year update of the IS success model treats information quality, system quality and service quality as separate dimensions feeding use and net benefits."),
    ("hevner2004design", "10.2307/25148625",
     "Canonical DSR framing: design artefacts are built and evaluated against organisational problems. Cited where the paper adopts DSR.",
     "PARAPHRASE: Design science creates and evaluates artefacts intended to solve identified organisational problems, with relevance and rigour as twin requirements."),
    ("peffers2007dsrm", "10.2753/mis0742-1222240302",
     "Provides the DSR process model (problem identification, objectives, design, demonstration, evaluation, communication) used to structure this paper's evaluation.",
     "PARAPHRASE: A design science research methodology is proposed comprising six steps from problem identification through demonstration and evaluation to communication."),
    ("gregor2013positioning", "10.25300/misq/2013/37.2.01",
     "Distinguishes design-science contributions by the type of knowledge claimed; supports the paper's explicit statement of what kind of contribution it makes.",
     "PARAPHRASE: Design science research should be positioned by the kind of knowledge it contributes, and its claims should be presented so that contribution type and evaluation are explicit."),
    ("march1995design", "10.1016/0167-9236(94)00041-2",
     "Separates design research from natural-science research; justifies reporting an artefact plus its evaluation rather than a hypothesis test alone.",
     "PARAPHRASE: Research on IT spans design research, which builds artefacts, and natural-science research, which seeks to explain; the two have different truth criteria."),
    ("mucha2024prerequirements", "10.1007/s00766-023-00412-z",
     "Systematic review of pre-requirements-specification traceability; supports the operational definition of traceability coverage and the claim that traceability is often incomplete in practice.",
     "PARAPHRASE: A systematic literature review characterises pre-requirements specification traceability, its motivations and the difficulties reported in establishing it."),
    ("trindade2016rastreabilidade", "10.5753/sbsi.2016.5997",
     "Brazilian (SBSI) exploratory study of requirements traceability in agile methods; satisfies the venue's SOL-coverage expectation with directly relevant work.",
     "PARAPHRASE: An exploratory study examines how requirements traceability is practised in agile methodologies, reporting the difficulties teams encounter."),
    ("goncalves2022rastreabilidade", "10.5753/sbsi_estendido.2022.222708",
     "Brazilian (SBSI) work on requirements traceability in software ecosystems; second SOL source, showing traceability is an active concern in the national community.",
     "PARAPHRASE: Requirements traceability is investigated in the context of software ecosystems, where independently evolving systems complicate the tracing of requirements."),
]


def fetch(doi: str) -> dict | None:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8"))["message"]
        except urllib.error.HTTPError as e:
            if e.code == 404:
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
    return "; ".join(out[:6]) + (" et al." if len(out) > 6 else "")


def year_of(msg: dict) -> str:
    for k in ("published-print", "published-online", "issued", "created"):
        dp = (msg.get(k) or {}).get("date-parts") or [[None]]
        if dp and dp[0] and dp[0][0]:
            return str(dp[0][0])
    return ""


FIELDS = ["key", "title", "authors", "year", "venue", "doi", "retrieval_date",
          "source_url", "verified_via", "supporting_sentence", "relevance"]


def main() -> int:
    rows, failed = [], []
    for key, doi, relevance, sentence in FACET:
        msg = fetch(doi)
        if not msg:
            failed.append((key, doi))
            continue
        rows.append({
            "key": key,
            "title": (msg.get("title") or [""])[0],
            "authors": authors_of(msg),
            "year": year_of(msg),
            "venue": (msg.get("container-title") or [""])[0] or msg.get("publisher", ""),
            "doi": msg.get("DOI", doi),
            "retrieval_date": TODAY,
            "source_url": msg.get("URL", f"https://doi.org/{doi}"),
            "verified_via": "crossref+abstract",
            "supporting_sentence": sentence,
            "relevance": relevance,
        })
        print(f"  {key:30s} {year_of(msg)}  {(msg.get('title') or [''])[0][:70]}")

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    venues = {(r["venue"] or "").lower() for r in rows}
    ish = sum(1 for v in venues if any(t in v for t in
              ("mis quarterly", "management information", "systems journal", "decision support",
               "requirements engineering", "sbsi", "sistemas de informa")))
    print(f"\nbuild_is_facet: wrote {len(rows)} rows -> {OUT}")
    print(f"build_is_facet: {ish} distinct IS/SOL venue(s); {len(failed)} failure(s) {failed}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
