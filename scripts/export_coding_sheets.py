#!/usr/bin/env python
"""Export BLINDED coding sheets for the two human-rater tasks.

Produces, under coding/:
    mutants_to_code.csv          item_id, repo, class, method, line, snippet, mutator, description, business_rule_relevant, notes
    stepdefs_to_code.csv         item_id, repo, file, line, expression, body_snippet, stepdef_class, mirror, notes
    _key_mutants.csv             item_id -> machine prediction (NOT for the rater)
    _key_stepdefs.csv            item_id -> machine prediction (NOT for the rater)
    MANIFEST.json                sampling frame, seed, counts, provenance

Blinding rules that this script enforces:
  * the rater sheets contain NO kill/survive status, so the mutant's outcome cannot bias the
    relevance judgement;
  * the machine's own predicted class is written only to the `_key_*` files, so a rater
    cannot anchor on the heuristic;
  * items are ordered by a seeded shuffle, not by repository or by any indicator value.

The mutant sample is drawn from the purpose-built feasibility suites, because the corpus
repositories never reached the mutation stage (no repository produced a green Gherkin
baseline). That is stated in MANIFEST.json rather than glossed over.

Usage:
    python scripts/export_coding_sheets.py --mutants 80 --stepdefs 80 --seed 20261125
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "metrics"))
OUT = os.path.join(ROOT, "coding")
PIT_DIRS = [
    os.path.join(ROOT, "pilot", "smoke-java", "target", "pit-aligned-aligned"),
    os.path.join(ROOT, "pilot", "smoke-java", "target", "pit-full-aligned"),
    os.path.join(ROOT, "pilot", "smoke-java", "target", "pit-test-defaults"),
]
REPOS = os.path.join(ROOT, "data", "repos")
CANDIDATES = os.path.join(ROOT, "data", "corpus", "candidates.csv")


def mutants_from_pit() -> list[dict]:
    seen: dict[str, dict] = {}
    for d in PIT_DIRS:
        xml = os.path.join(d, "mutations.xml")
        if not os.path.exists(xml):
            continue
        try:
            root = ET.parse(xml).getroot()
        except Exception:
            continue
        for m in root.iter("mutation"):
            key = "|".join([
                m.findtext("mutatedClass", ""), m.findtext("mutatedMethod", ""),
                m.findtext("lineNumber", ""), m.findtext("mutator", ""),
                m.findtext("description", ""),
            ])
            if key in seen:
                continue
            seen[key] = {
                "repo": "feasibility-java",
                "class": m.findtext("mutatedClass", ""),
                "method": m.findtext("mutatedMethod", ""),
                "line": m.findtext("lineNumber", ""),
                "mutator": m.findtext("mutator", ""),
                "description": (m.findtext("description", "") or "").strip()[:200],
                "snippet": (m.findtext("sourceFile", "") or "").strip()[:80],
            }
    return list(seen.values())


def stepdefs_from_repos(limit_repos: int) -> tuple[list[dict], list[dict]]:
    """Return (blinded_items, keyed_predictions) by scanning working copies."""
    import static_metrics as sm  # local import: heavy module

    items: list[dict] = []
    keys: list[dict] = []
    if not os.path.exists(CANDIDATES):
        return items, keys
    with open(CANDIDATES, newline="", encoding="utf-8") as f:
        eligible = [r["repo"] for r in csv.DictReader(f) if r.get("state") == "eligible"]
    used = 0
    for repo in eligible:
        if used >= limit_repos:
            break
        d = os.path.join(REPOS, repo.replace("/", "__", 1))
        if not os.path.isdir(d):
            continue
        try:
            _row, audit = sm.compute(repo, d)
        except Exception:
            continue
        used += 1
        for a in audit:
            body = (a.get("weak_kinds") or "")
            items.append({
                "repo": repo,
                "file": a.get("file", ""),
                "line": a.get("line", ""),
                "expression": (a.get("expression") or "")[:160],
                # The body itself is not stored in the audit; the rater sees the expression
                # and the location, and is told to open the file at that line.
                "body_snippet": f"open {a.get('file','')} at line {a.get('line','')}",
            })
            keys.append({"machine_class": a.get("class", ""),
                         "machine_weak_kinds": body})
    return items, keys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mutants", type=int, default=80)
    ap.add_argument("--stepdefs", type=int, default=80)
    ap.add_argument("--seed", type=int, default=20261125)
    ap.add_argument("--repos", type=int, default=5, help="repositories to mine for step definitions")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    rng = random.Random(a.seed)

    # ---- mutants
    muts = mutants_from_pit()
    rng.shuffle(muts)
    muts = muts[: a.mutants]
    for i, m in enumerate(muts, 1):
        m["item_id"] = f"M{i:03d}"
    with open(os.path.join(OUT, "mutants_to_code.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["item_id", "repo", "class", "method", "line", "mutator", "description",
                    "business_rule_relevant", "notes"])
        for m in muts:
            w.writerow([m["item_id"], m["repo"], m["class"], m["method"], m["line"],
                        m["mutator"], m["description"], "", ""])
    with open(os.path.join(OUT, "_key_mutants.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["item_id", "machine_prediction"])
        for m in muts:
            w.writerow([m["item_id"], "NO_MACHINE_PREDICTION"])  # relevance is not automated

    # ---- step definitions
    items, keys = stepdefs_from_repos(a.repos)
    rng.shuffle(items)
    items, keys = items[: a.stepdefs], keys[: a.stepdefs]
    for i, it in enumerate(items, 1):
        it["item_id"] = f"S{i:03d}"
    with open(os.path.join(OUT, "stepdefs_to_code.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["item_id", "repo", "file", "line", "expression", "body_snippet",
                    "stepdef_class", "mirror", "notes"])
        for it in items:
            w.writerow([it["item_id"], it["repo"], it["file"], it["line"],
                        it["expression"], it["body_snippet"], "", ""])
    with open(os.path.join(OUT, "_key_stepdefs.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["item_id", "machine_class", "machine_weak_kinds"])
        for it, k in zip(items, keys):
            w.writerow([it["item_id"], k["machine_class"], k["machine_weak_kinds"]])

    digest = hashlib.sha256(
        "\n".join(m["item_id"] + m["description"] for m in muts).encode()
    ).hexdigest()[:16]
    manifest = {
        "seed": a.seed,
        "mutant_items": len(muts),
        "stepdef_items": len(items),
        "mutant_source": "purpose-built feasibility suites (PIT mutations.xml); the corpus "
                         "repositories never reached the mutation stage, so no corpus mutants exist",
        "stepdef_source": f"up to {a.repos} statically eligible repositories with working copies",
        "blinding": "no kill/survive status and no machine prediction appears in the rater sheets",
        "item_order": "seeded random shuffle",
        "sample_sha256_16": digest,
        "human_action_required": [
            "Two independent raters complete mutants_to_code.csv and stepdefs_to_code.csv.",
            "Run scripts/compute_irr.py on the two completed copies.",
            "Only then may the manuscript report a kappa.",
        ],
    }
    with open(os.path.join(OUT, "MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(json.dumps({k: manifest[k] for k in
                      ("seed", "mutant_items", "stepdef_items", "sample_sha256_16")}, indent=2))
    print(f"wrote sheets to {OUT}")
    if not items:
        print("WARNING: no step definitions were mined; check that working copies exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
