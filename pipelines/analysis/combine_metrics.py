#!/usr/bin/env python
"""Combine per-mutant statuses into the repository-level analysis table.

Per-mode scores follow the protocol:

    MS_all(mode)    = (K+T) / (K+S+T+NC)
    MS_cov(mode)    = (K+T) / (K+S+T)
    mutant_coverage = (K+S+T) / (K+S+T+NC)

Differential kill uses THREE execution modes (BDD, NON_BDD, FULL) and is delegated to
`pipelines/analysis/differential.py`, which is unit-tested. The comparison set is

    S = executed(BDD) INTERSECT executed(NON_BDD)

so that all three modes are simultaneously defined on S and FULL kill decomposes
exactly as K_FULL = K_BDD union K_NON_BDD. On S:

    DK_bdd_uplift    = MS_cov(FULL,S) - MS_cov(NON_BDD,S) = |K_BDD \\ K_NON_BDD| / |S|
    DK_nonbdd_uplift = MS_cov(FULL,S) - MS_cov(BDD,S)     = |K_NON_BDD \\ K_BDD| / |S|
    Overlap          = |K_BDD & K_NON_BDD| / |K_FULL|
    BDD_unique_share = |K_BDD \\ K_NON_BDD| / |K_FULL|
    BDD_total_share  = |K_BDD| / |K_FULL|

An earlier version defined `DK_norm = MS_cov(FULL) - MS_cov(BDD)` and called it the
uplift *of* BDD. That is the uplift of the non-BDD tests: it is large when BDD is
decorative and zero when BDD is the only thing detecting a fault. It is retained only as
`DK_inverted_legacy` so the correction is auditable in the output table.

TIMEOUT counts as detected; INVALID is excluded from every denominator and counted.
Coverage containment and FULL-kill decomposability are asserted per repository and
flagged, never assumed silently.

Outputs:
    data/metrics/repo_level.csv     one row per repository (the analysis unit)
"""
from __future__ import annotations

import csv
import glob
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from differential import compute_differential  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MUT = os.path.join(ROOT, "data", "mutants")
STATIC = os.path.join(ROOT, "data", "metrics", "static_indicators.csv")
OUT = os.path.join(ROOT, "data", "metrics", "repo_level.csv")


def load_mode(repo_slug: str, mode: str) -> dict[str, str]:
    p = os.path.join(MUT, f"{repo_slug}.{mode}.csv")
    if not os.path.exists(p):
        return {}
    out = {}
    with open(p, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[r["mutant_id"]] = r["status"]
    return out


def scores(statuses: Counter, detect_timeouts: bool = True) -> dict:
    k = statuses.get("KILLED", 0)
    s = statuses.get("SURVIVED", 0)
    t = statuses.get("TIMEOUT", 0)
    nc = statuses.get("NO_COVERAGE", 0)
    num = k + (t if detect_timeouts else 0)
    den_all = k + s + t + nc
    den_cov = k + s + t
    return {
        "killed": k, "survived": s, "timeout": t, "no_coverage": nc,
        "invalid_excluded": statuses.get("INVALID", 0),
        "total": den_all,
        "MS_all": (num / den_all) if den_all else None,
        "MS_cov": (num / den_cov) if den_cov else None,
        "mutant_coverage": ((k + s + t) / den_all) if den_all else None,
    }


def main() -> int:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    bdd_files = sorted(glob.glob(os.path.join(MUT, "*.bdd.csv")))
    if not bdd_files:
        print("combine: no BDD mutation files found")
        return 1

    static: dict[str, dict] = {}
    if os.path.exists(STATIC):
        with open(STATIC, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                static[r["repo"]] = r

    rows = []
    for bp in bdd_files:
        base = os.path.basename(bp)[:-len(".bdd.csv")]
        with open(bp, newline="", encoding="utf-8") as f:
            first = next(csv.DictReader(f), None)
        repo = first["repo"] if first else base.replace("__", "/", 1)

        bdd = load_mode(base, "bdd")
        nonbdd = load_mode(base, "nonbdd")
        full = load_mode(base, "full")
        if not bdd:
            continue
        bc = Counter(bdd.values())
        bdd_scores = scores(bc)

        row = {
            "repo": repo,
            "language": first.get("language", "") if first else "",
            "n_mutants_bdd": len(bdd),
            **{f"bdd_{k}": v for k, v in bdd_scores.items()},
        }

        if nonbdd:
            row["n_mutants_nonbdd"] = len(nonbdd)
            row["nonbdd_MS_cov"] = scores(Counter(nonbdd.values()))["MS_cov"]
            row["nonbdd_mutant_coverage"] = scores(Counter(nonbdd.values()))["mutant_coverage"]

        if full:
            row.update({f"full_{k}": v for k, v in scores(Counter(full.values())).items()})

        if nonbdd:
            d = compute_differential(bdd, nonbdd, full if full else None)
            row.update({f"dk_{k}": v for k, v in d.as_dict().items()})
            # The inverted legacy quantity, kept only for auditability of the correction.
            if d.ms_cov_full is not None and d.ms_cov_bdd is not None:
                row["DK_inverted_legacy"] = d.ms_cov_full - d.ms_cov_bdd
        else:
            row["dk_note"] = "nonbdd mode unavailable: three-mode decomposition not computable"

        st = static.get(repo, {})
        for k in ("D1_skip_ratio", "D2_assertion_weakness_ratio", "D2_confidence",
                  "D3_stale_spec_ratio", "D4_redundancy_cluster_ratio",
                  "D5_glue_duplication_ratio", "D6_literal_bearing_stepdef_ratio",
                  "D7_mirror_stepdef_ratio", "n_scenarios", "n_active_scenarios",
                  "n_features", "n_step_defs", "n_domain_files", "domain_tier"):
            if k in st:
                row[k] = st[k]
        rows.append(row)

    if not rows:
        print("combine: nothing to combine")
        return 1

    # Union of columns, preserving first-seen order for readability.
    cols: list[str] = []
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    print(json.dumps({
        "repos": len(rows),
        "with_three_modes": sum(1 for r in rows if r.get("dk_s_size") is not None),
        "with_full_suite": sum(1 for r in rows if r.get("full_MS_cov") is not None),
        "empty_comparison_set": sum(1 for r in rows if r.get("dk_s_size") == 0),
        "containment_failures": sum(1 for r in rows if r.get("dk_containment_ok") is False),
        "mode_integrity_failures": sum(
            1 for r in rows if r.get("dk_mode_integrity_ok") is False),
        "out": OUT,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
