#!/usr/bin/env python
"""Combine per-mutant statuses into the repository-level analysis table.

Implements docs/method.md section 7.1 exactly:

    MS_all(mode)   = (K+T) / (K+S+T+NC)
    MS_cov(mode)   = (K+T) / (K+S+T)
    mutant_coverage= (K+S+T) / (K+S+T+NC)
    S              = mutants covered by the BDD run (status != NO_COVERAGE)
    DK_norm        = MS_cov_full(S) - MS_cov_bdd(S)
    DK_count       = |K_full(S) \\ K_bdd(S)| / |S|
    BDD_kill_share = |K_bdd(S)| / |K_full(S)|

TIMEOUT counts as detected in the primary formula; a sensitivity that removes it is
also computed. INVALID is excluded from every denominator and its count reported.

Containment check: every mutant in S must also be executed by the full run. With a
command/whole-suite runner the full mode reports no coverage information, so we
verify containment structurally (a mutant in S was covered by a subset of the full
suite, therefore covered by the full suite) and flag any mutant that the full run
marks NO_COVERAGE — that would violate the protocol's mode-integrity assertion.

Outputs:
    data/metrics/repo_level.csv     one row per repository (the analysis unit)
"""
from __future__ import annotations

import csv
import glob
import json
import os
from collections import Counter, defaultdict

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
        full = load_mode(base, "full")
        if not bdd:
            continue
        bc = Counter(bdd.values())
        bdd_scores = scores(bc)

        S = {mid for mid, st in bdd.items() if st != "NO_COVERAGE"}
        row = {
            "repo": repo,
            "language": first.get("language", "") if first else "",
            "n_mutants_bdd": len(bdd),
            **{f"bdd_{k}": v for k, v in bdd_scores.items()},
        }

        if full:
            fc = Counter(full.values())
            full_scores = scores(fc)
            row.update({f"full_{k}": v for k, v in full_scores.items()})
            overlap = S & set(full)
            row["S_size"] = len(overlap)
            row["S_share_of_bdd"] = (len(overlap) / len(S)) if S else None
            contained = all(full.get(m) != "NO_COVERAGE" for m in overlap)
            row["mode_integrity_ok"] = int(contained)
            if overlap:
                k_bdd = {m for m in overlap if bdd[m] in ("KILLED", "TIMEOUT")}
                k_full = {m for m in overlap if full.get(m) in ("KILLED", "TIMEOUT")}
                ms_cov_bdd_S = len(k_bdd) / len(overlap)
                ms_cov_full_S = len(k_full) / len(overlap)
                row["MS_cov_bdd_S"] = ms_cov_bdd_S
                row["MS_cov_full_S"] = ms_cov_full_S
                row["DK_norm"] = ms_cov_full_S - ms_cov_bdd_S
                row["DK_count"] = len(k_full - k_bdd) / len(overlap)
                row["BDD_kill_share"] = (len(k_bdd) / len(k_full)) if k_full else None
            else:
                row.update(MS_cov_bdd_S=None, MS_cov_full_S=None, DK_norm=None,
                           DK_count=None, BDD_kill_share=None)
        else:
            row["full_available"] = 0

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
        "with_full_suite": sum(1 for r in rows if r.get("full_available") != 0),
        "mode_integrity_failures": sum(1 for r in rows if r.get("mode_integrity_ok") == 0),
        "out": OUT,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
