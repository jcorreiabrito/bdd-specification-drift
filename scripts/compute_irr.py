#!/usr/bin/env python
"""Cohen's kappa for two independently coded sheets, with a bootstrap 95% CI.

This script exists so that the study never has to invent a reliability statistic. It is
deliberately strict:

  * it refuses to run if the two raters did not code the same item set (kappa on mismatched
    item sets is meaningless);
  * blank cells are treated as MISSING, not as a negative label, and the count is reported;
  * it reports observed agreement and both marginal distributions alongside kappa, because a
    kappa can look respectable while one rater used a single label throughout
    (the prevalence problem);
  * `unclear` is only valid for the D7 column and is excluded from kappa.

Outputs a JSON block and, on request, LaTeX macros for the manuscript.

Usage:
    python scripts/compute_irr.py --a a.csv --b b.csv --label-column business_rule_relevant
    python scripts/compute_irr.py --a a.csv --b b.csv --label-column stepdef_class --macros
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import sys

NEVER_LABELS = {"", "unclear", "na", "n/a", "?"}


def load(path: str, col: str) -> dict[str, str]:
    out: dict[str, str] = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if col not in (reader.fieldnames or []):
            raise SystemExit(f"{path}: column '{col}' not found; columns are {reader.fieldnames}")
        for row in reader:
            item = (row.get("item_id") or "").strip()
            if not item:
                continue
            out[item] = (row.get(col) or "").strip().lower()
    return out


def cohen_kappa(a: list[str], b: list[str]) -> float | None:
    n = len(a)
    if n == 0:
        return None
    labels = sorted(set(a) | set(b))
    observed = sum(1 for x, y in zip(a, b) if x == y) / n
    pa = {l: a.count(l) / n for l in labels}
    pb = {l: b.count(l) / n for l in labels}
    expected = sum(pa[l] * pb[l] for l in labels)
    if math.isclose(expected, 1.0):
        # Both raters used one identical label throughout: kappa is undefined (0/0).
        return None
    return (observed - expected) / (1 - expected)


def bootstrap_ci(a: list[str], b: list[str], reps: int = 2000, seed: int = 20261125):
    rng = random.Random(seed)
    n = len(a)
    if n < 5:
        return (None, None)
    vals = []
    for _ in range(reps):
        idx = [rng.randrange(n) for _ in range(n)]
        k = cohen_kappa([a[i] for i in idx], [b[i] for i in idx])
        if k is not None:
            vals.append(k)
    if not vals:
        return (None, None)
    vals.sort()
    return (vals[int(0.025 * (len(vals) - 1))], vals[int(0.975 * (len(vals) - 1))])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="completed sheet from rater A")
    ap.add_argument("--b", required=True, help="completed sheet from rater B")
    ap.add_argument("--label-column", required=True)
    ap.add_argument("--macros", action="store_true",
                    help="also write LaTeX macros to paper/numbers_irr.tex")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    A = load(args.a, args.label_column)
    B = load(args.b, args.label_column)

    only_a = set(A) - set(B)
    only_b = set(B) - set(A)
    if only_a or only_b:
        print(f"REFUSING: item sets differ. only_in_A={len(only_a)} only_in_B={len(only_b)}")
        for x in list(only_a)[:5]:
            print("  only in A:", x)
        for x in list(only_b)[:5]:
            print("  only in B:", x)
        return 2

    shared = sorted(set(A) & set(B))
    pairs = [(A[i], B[i]) for i in shared]
    usable = [(x, y) for x, y in pairs
              if x not in NEVER_LABELS and y not in NEVER_LABELS]
    missing = len(pairs) - len(usable)

    a = [x for x, _ in usable]
    b = [y for _, y in usable]
    kappa = cohen_kappa(a, b)
    lo, hi = bootstrap_ci(a, b)
    observed = (sum(1 for x, y in zip(a, b) if x == y) / len(a)) if a else None

    def dist(v):
        d: dict[str, int] = {}
        for s in v:
            d[s] = d.get(s, 0) + 1
        return d

    result = {
        "label_column": args.label_column,
        "items_shared": len(shared),
        "items_coded_by_both": len(usable),
        "excluded_missing_or_unclear": missing,
        "observed_agreement": round(observed, 4) if observed is not None else None,
        "cohen_kappa": round(kappa, 4) if kappa is not None else None,
        "kappa_ci95": [round(lo, 4) if lo is not None else None,
                       round(hi, 4) if hi is not None else None],
        "distribution_A": dist(a),
        "distribution_B": dist(b),
        "rater_files": [os.path.basename(args.a), os.path.basename(args.b)],
    }

    print(json.dumps(result, indent=2))
    if kappa is None:
        print("\nNOTE: kappa is undefined (single label used by both raters, or too few "
              "usable items). Report that, not a number.")
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"wrote {args.out}")

    if args.macros:
        if kappa is None or lo is None:
            print("\nREFUSING to emit macros: no defined kappa. The manuscript must state that "
                  "reliability was not established, not carry a placeholder number.")
            return 1
        name = args.label_column.replace("_", "")
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "paper", "numbers_irr.tex")
        with open(path, "w", encoding="utf-8") as f:
            f.write("% GENERATED by scripts/compute_irr.py from real human coding sheets.\n")
            f.write("% Do not edit. If this file is absent, no human reliability data exists.\n")
            f.write(f"\\newcommand{{\\Kappa{name}}}{{{kappa:.3f}}}\n")
            f.write(f"\\newcommand{{\\Kappa{name}Lo}}{{{lo:.3f}}}\n")
            f.write(f"\\newcommand{{\\Kappa{name}Hi}}{{{hi:.3f}}}\n")
            f.write(f"\\newcommand{{\\Kappa{name}N}}{{{len(usable)}}}\n")
        print(f"wrote {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
