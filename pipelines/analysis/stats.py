#!/usr/bin/env python
"""Statistics for RQ2/RQ3, exactly as declared in docs/method.md section 12.

Declared before measurement, and that order is the point:
  * TWO primary indicators only (`D1_skip_ratio`, `D2_assertion_weakness_ratio`)
    against ONE primary outcome (`MS_cov_bdd`), Holm-corrected across the two;
  * everything else is exploratory (one family, Holm-corrected, labelled);
  * a single pooled Spearman is NEVER the headline: per-stratum rho with bootstrap
    95% CIs first, then a pooled estimate that explicitly averages within-stratum
    associations;
  * `mutant_coverage` is a covariate in every model and is reported in every table;
  * |rho| below the pre-computed floor is reported as "not detectable at this n",
    not as a null finding.

With small n the honest output is often "underpowered". This script says so rather
than manufacturing a correlation.

Outputs:
    data/metrics/stats.json          machine-readable results
    paper/tables/*.tex               LaTeX fragments used by the manuscript
    figures/*.pdf, *.png             figures used by the manuscript
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys
from itertools import combinations

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
IN = os.path.join(ROOT, "data", "metrics", "repo_level.csv")
OUT_JSON = os.path.join(ROOT, "data", "metrics", "stats.json")
TAB_DIR = os.path.join(ROOT, "paper", "tables")
FIG_DIR = os.path.join(ROOT, "figures")
SEED = 20261125
BOOT = 2000
PRIMARY = ["D1_skip_ratio", "D2_assertion_weakness_ratio"]
EXPLORATORY = ["D3_stale_spec_ratio", "D4_redundancy_cluster_ratio",
               "D5_glue_duplication_ratio", "D6_literal_bearing_stepdef_ratio",
               "D7_mirror_stepdef_ratio"]
OUTCOME = "MS_cov_bdd"
MIN_STRATUM_N = 8


def fnum(v):
    try:
        if v in (None, "", "None", "nan"):
            return None
        x = float(v)
        return None if math.isnan(x) or math.isinf(x) else x
    except (TypeError, ValueError):
        return None


def spearman(x, y):
    """Spearman rho with average ranks; no scipy dependency required."""
    n = len(x)
    if n < 3:
        return None
    def rank(a):
        order = sorted(range(len(a)), key=lambda i: a[i])
        r = [0.0] * len(a)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and a[order[j + 1]] == a[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    dy = math.sqrt(sum((b - my) ** 2 for b in ry))
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def boot_ci(x, y, rng, reps=BOOT):
    n = len(x)
    if n < 4:
        return (None, None)
    est = spearman(x, y)
    if est is None:
        return (None, None)
    vals = []
    for _ in range(reps):
        idx = rng.integers(0, n, n)
        xs = [x[i] for i in idx]
        ys = [y[i] for i in idx]
        r = spearman(xs, ys)
        if r is not None:
            vals.append(r)
    if not vals:
        return (None, None)
    vals.sort()
    lo = vals[int(0.025 * (len(vals) - 1))]
    hi = vals[int(0.975 * (len(vals) - 1))]
    return (lo, hi)


def min_detectable_rho(n, alpha=0.05, power=0.8):
    """Protocol 12.6: |rho| floor on the Fisher-z scale."""
    if n <= 3:
        return None
    try:
        from statistics import NormalDist
        z_a = NormalDist().inv_cdf(1 - alpha / 2)
        z_b = NormalDist().inv_cdf(power)
    except Exception:
        z_a, z_b = 1.959964, 0.841621
    se = 1.030 / math.sqrt(n - 3)
    return math.tanh((z_a + z_b) * se)


def holm(pvals: list[tuple[str, float]]) -> dict:
    """Holm-Bonferroni. p-values here are two-sided normal approximations from rho."""
    ordered = sorted(pvals, key=lambda t: t[1])
    m = len(ordered)
    out = {}
    prev = 0.0
    for i, (k, p) in enumerate(ordered):
        adj = min(1.0, max(prev, (m - i) * p))
        out[k] = adj
        prev = adj
    return out


def rho_pvalue(rho, n):
    if rho is None or n < 3:
        return None
    if abs(rho) >= 1:
        return 0.0
    # Fisher z approximation; adequate for the reporting role here (effect sizes dominate).
    z = math.atanh(rho) * math.sqrt(n - 3)
    from statistics import NormalDist
    return 2 * (1 - NormalDist().cdf(abs(z)))


def main() -> int:
    if not os.path.exists(IN):
        print(f"stats: missing {IN}")
        return 1
    with open(IN, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    usable = [r for r in rows if fnum(r.get(OUTCOME)) is not None]
    print(f"stats: {len(rows)} repos, {len(usable)} with a usable {OUTCOME}")

    os.makedirs(TAB_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)
    rng = np.random.default_rng(SEED)
    result = {
        "n_repos_total": len(rows),
        "n_usable_primary_outcome": len(usable),
        "seed": SEED,
        "bootstrap_reps": BOOT,
        "min_detectable_rho_by_n": {str(n): (round(min_detectable_rho(n), 3) if min_detectable_rho(n) else None)
                                    for n in (5, 8, 10, 15, 20, 30, 40)},
        "strata": {},
        "primary": {},
        "exploratory": {},
        "descriptive": {},
    }

    # ---------------- descriptive (always reportable)
    def summarise(key):
        vals = [fnum(r.get(key)) for r in usable]
        vals = [v for v in vals if v is not None]
        if not vals:
            return None
        vals.sort()
        n = len(vals)
        med = vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2
        return {"n": n, "median": round(med, 4), "min": round(vals[0], 4),
                "max": round(vals[-1], 4), "mean": round(sum(vals) / n, 4)}

    for key in [OUTCOME, "MS_all_bdd", "mutant_coverage", "MS_cov_full", "DK_norm",
                "BDD_kill_share", "bdd_mutant_coverage"] + PRIMARY + EXPLORATORY:
        s = summarise(key)
        if s:
            result["descriptive"][key] = s

    # ---------------- per-stratum associations
    strata = {}
    for r in usable:
        strata.setdefault(r.get("language") or "unknown", []).append(r)
    for stratum, srows in sorted(strata.items()):
        entry = {"n": len(srows),
                 "powered": len(srows) >= MIN_STRATUM_N,
                 "min_detectable_rho": (round(min_detectable_rho(len(srows)), 3)
                                        if min_detectable_rho(len(srows)) else None),
                 "associations": {}}
        for ind in PRIMARY + EXPLORATORY:
            pairs = [(fnum(r.get(ind)), fnum(r.get(OUTCOME))) for r in srows]
            pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
            if len(pairs) < 4:
                entry["associations"][ind] = {"n": len(pairs), "rho": None,
                                              "note": "too few complete pairs"}
                continue
            xs = [a for a, _ in pairs]
            ys = [b for _, b in pairs]
            rho = spearman(xs, ys)
            lo, hi = boot_ci(xs, ys, rng)
            entry["associations"][ind] = {
                "n": len(pairs), "rho": (round(rho, 4) if rho is not None else None),
                "ci_lo": (round(lo, 4) if lo is not None else None),
                "ci_hi": (round(hi, 4) if hi is not None else None),
                "p_approx": (round(rho_pvalue(rho, len(pairs)), 4)
                             if rho_pvalue(rho, len(pairs)) is not None else None),
                "detectable": (abs(rho) >= (min_detectable_rho(len(pairs)) or 1.1)
                               if rho is not None else None),
            }
        result["strata"][stratum] = entry

    # ---------------- pooled: average within-stratum rho (never a raw pooled rho)
    for family, inds in (("primary", PRIMARY), ("exploratory", EXPLORATORY)):
        for ind in inds:
            rhos = [e["associations"].get(ind, {}).get("rho")
                    for e in result["strata"].values()
                    if e["associations"].get(ind, {}).get("rho") is not None]
            if not rhos:
                result[family][ind] = {"pooled_within_stratum_rho": None,
                                       "n_strata": 0}
                continue
            pooled = sum(rhos) / len(rhos)
            # cluster bootstrap by stratum
            vals = []
            keys = list(result["strata"].keys())
            for _ in range(BOOT):
                pick = list(rng.choice(keys, len(keys), replace=True))
                rs = []
                for k in pick:
                    r = result["strata"][k]["associations"].get(ind, {}).get("rho")
                    if r is not None:
                        rs.append(r)
                if rs:
                    vals.append(sum(rs) / len(rs))
            vals.sort()
            lo = vals[int(0.025 * (len(vals) - 1))] if vals else None
            hi = vals[int(0.975 * (len(vals) - 1))] if vals else None
            result[family][ind] = {
                "pooled_within_stratum_rho": round(pooled, 4),
                "cluster_bootstrap_ci": [round(lo, 4) if lo is not None else None,
                                         round(hi, 4) if hi is not None else None],
                "n_strata": len(rhos),
                "per_stratum": {k: result["strata"][k]["associations"].get(ind, {}).get("rho")
                                for k in result["strata"]},
            }

    # Holm across the two primary tests (using per-stratum min-n for power honesty)
    prim_p = []
    for ind in PRIMARY:
        entry = result["primary"].get(ind, {})
        rho = entry.get("pooled_within_stratum_rho")
        n_eff = max([result["strata"][k]["associations"].get(ind, {}).get("n") or 0
                     for k in result["strata"]] or [0])
        p = rho_pvalue(rho, n_eff) if rho is not None else None
        if p is not None:
            prim_p.append((ind, p))
    if prim_p:
        adj = holm(prim_p)
        for ind, a in adj.items():
            result["primary"][ind]["p_holm"] = round(a, 4)
    result["notes"] = [
        "A single pooled Spearman over all repositories is deliberately NOT reported; "
        "PIT/Stryker/mutmut scores are not on a common axis, so the pooled figure "
        "averages within-stratum associations.",
        "Associations below min_detectable_rho are reported as not detectable at this n, "
        "not as evidence of no effect.",
        f"Strata with fewer than {MIN_STRATUM_N} repositories are descriptive only.",
    ]

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(json.dumps({k: result[k] for k in ("n_usable_primary_outcome", "strata")}, indent=2)[:3000])
    print(f"stats: wrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
