#!/usr/bin/env python
"""Zero-build static census of the seven drift indicators over ALL eligible repositories.

The point of this stage is that it requires no builds, no container, and no network: it runs
the indicator extractors directly over the working copies already on disk. It was omitted
from the first submission, which left RQ1's measurement half-evaluated even though the data
were free.

ROBUSTNESS. A single-process loop over 94 repositories is not safe: a handful of working
copies contain pathological inputs (very large trees, or a scenario-overlap graph that is
quadratic in scenario count) and one such repository can block the whole census. So the
default mode spawns ONE SUBPROCESS PER REPOSITORY with a hard timeout. A repository that
exceeds the budget is recorded as `timeout` and excluded from the summary with its count
disclosed — never silently dropped, and never allowed to stop the other 93.

Reports, per indicator: n, undefined count, median, IQR, min, max. A missing indicator is
reported as missing, never imputed.

Outputs:
    data/metrics/static_indicators.csv     one row per repository (deduped on re-run)
    data/metrics/census.json               summary statistics + per-repository status
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "metrics"))

CANDIDATES = os.path.join(ROOT, "data", "corpus", "candidates.csv")
REPOS = os.path.join(ROOT, "data", "repos")
OUT_CSV = os.path.join(ROOT, "data", "metrics", "static_indicators.csv")
OUT_JSON = os.path.join(ROOT, "data", "metrics", "census.json")

INDICATORS = [
    "D1_skip_ratio", "D2_assertion_weakness_ratio", "D3_stale_spec_ratio",
    "D4_redundancy_cluster_ratio", "D5_glue_duplication_ratio",
    "D6_literal_bearing_stepdef_ratio", "D7_mirror_stepdef_ratio",
]


def quantile(sorted_vals: list[float], q: float) -> float:
    if not sorted_vals:
        raise ValueError("empty")
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    pos = (len(sorted_vals) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] * (1 - (pos - lo)) + sorted_vals[hi] * (pos - lo)


def disable_d3() -> None:
    """Make D3 fail fast.

    D3 needs `git blame` over every scenario's line range. Only a minority of working
    copies carry VCS history at all, and on those the blame calls dominate run time by
    orders of magnitude. Rather than let one indicator block the other six, --skip-d3 makes
    the history probe fail immediately so D3 is recorded as undefined for every repository.
    Undefined is reported as undefined, never imputed as zero.
    """
    import static_metrics as sm
    sm.git = lambda *_a, **_k: (1, "")


def compute_one(repo: str, skip_d3: bool) -> dict | None:
    import static_metrics as sm
    if skip_d3:
        sm.git = lambda *_a, **_k: (1, "")
    d = os.path.join(REPOS, repo.replace("/", "__", 1))
    if not os.path.isdir(d):
        return None
    row, _audit = sm.compute(repo, d)
    return row


def run_driver(args) -> int:
    if not os.path.exists(CANDIDATES):
        print(f"census: missing {CANDIDATES}")
        return 1
    with open(CANDIDATES, newline="", encoding="utf-8") as f:
        eligible = [r["repo"] for r in csv.DictReader(f) if r.get("state") == "eligible"]
    print(f"census: {len(eligible)} eligible repositories, "
          f"per-repo timeout {args.timeout}s")

    rows: list[dict] = []
    status: dict[str, str] = {}
    for i, repo in enumerate(eligible, 1):
        d = os.path.join(REPOS, repo.replace("/", "__", 1))
        if not os.path.isdir(d):
            status[repo] = "no_working_copy"
            continue
        cmd = [sys.executable, os.path.abspath(__file__), "--only", repo]
        if args.skip_d3:
            cmd.append("--skip-d3")
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=args.timeout)
        except subprocess.TimeoutExpired:
            status[repo] = "timeout"
            print(f"  [{i:3d}/{len(eligible)}] {repo}: TIMEOUT")
            continue
        line = (p.stdout or "").strip().splitlines()
        payload = line[-1] if line else ""
        if p.returncode == 0 and payload.startswith("{"):
            rows.append(json.loads(payload))
            status[repo] = "ok"
            if i % 10 == 0:
                print(f"  [{i:3d}/{len(eligible)}] {len(rows)} measured", flush=True)
        else:
            status[repo] = "error"
            print(f"  [{i:3d}/{len(eligible)}] {repo}: ERROR {(p.stderr or '')[-120:]}")

    return summarise(rows, eligible, status, args)


def summarise(rows: list[dict], eligible: list[str], status: dict[str, str],
              args) -> int:
    # Merge with any rows already on disk so re-runs are incremental.
    existing: dict[str, dict] = {}
    if os.path.exists(OUT_CSV):
        with open(OUT_CSV, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                existing[r["repo"]] = r
    merged = dict(existing)
    for r in rows:
        merged[r["repo"]] = r

    if merged:
        cols: list[str] = []
        for r in merged.values():
            for k in r:
                if k not in cols:
                    cols.append(k)
        os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
        with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(merged.values())

    measured = list(merged.values())
    summary: dict = {
        "eligible_repositories": len(eligible),
        "measured": len(measured),
        "newly_measured_this_run": len(rows),
        "status_counts": {s: sum(1 for v in status.values() if v == s)
                          for s in sorted(set(status.values()))},
        "no_working_copy": sum(1 for v in status.values() if v == "no_working_copy"),
        "timeouts": [k for k, v in status.items() if v == "timeout"],
        "d3_status": "disabled (no VCS history for most working copies)",
        "indicators": {},
    }
    for ind in INDICATORS:
        vals, missing = [], 0
        for r in measured:
            v = r.get(ind)
            if v in (None, "", "None"):
                missing += 1
                continue
            try:
                vals.append(float(v))
            except (TypeError, ValueError):
                missing += 1
        vals.sort()
        if vals:
            summary["indicators"][ind] = {
                "n": len(vals), "undefined": missing,
                "median": round(quantile(vals, 0.5), 4),
                "q1": round(quantile(vals, 0.25), 4),
                "q3": round(quantile(vals, 0.75), 4),
                "min": round(vals[0], 4), "max": round(vals[-1], 4),
            }
        else:
            summary["indicators"][ind] = {"n": 0, "undefined": missing}

    summary["D2_low_confidence"] = sum(
        1 for r in measured if r.get("D2_confidence") == "low_confidence")
    tiers: dict[str, int] = {}
    for r in measured:
        tiers[r.get("domain_tier", "?")] = tiers.get(r.get("domain_tier", "?"), 0) + 1
    summary["domain_tier_counts"] = tiers

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n=== static census (zero builds) ===")
    print(f"{'indicator':34s} {'n':>4s} {'undef':>6s} {'median':>8s} {'IQR':>18s}")
    for ind in INDICATORS:
        s = summary["indicators"][ind]
        if s["n"]:
            iqr = f"[{s['q1']:.3f}, {s['q3']:.3f}]"
            print(f"{ind:34s} {s['n']:4d} {s['undefined']:6d} {s['median']:8.3f} {iqr:>18s}")
        else:
            print(f"{ind:34s} {0:4d} {s['undefined']:6d} {'-':>8s} {'-':>18s}")
    print(f"\nmeasured {summary['measured']}/{summary['eligible_repositories']}; "
          f"status {summary['status_counts']}")
    print(f"wrote {OUT_CSV} and {OUT_JSON}")
    return 0 if summary["measured"] else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None,
                    help="compute a single repository and print its row as JSON")
    ap.add_argument("--skip-d3", action="store_true")
    ap.add_argument("--timeout", type=int, default=90, help="per-repository seconds")
    args = ap.parse_args()

    if args.only:
        row = compute_one(args.only, args.skip_d3)
        if row is None:
            return 1
        print(json.dumps(row))
        return 0
    return run_driver(args)


if __name__ == "__main__":
    sys.exit(main())
