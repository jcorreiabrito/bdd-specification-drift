#!/usr/bin/env python
"""Assemble the three-mode feasibility evidence for both ecosystems.

Reads what the two harnesses produced and computes the corrected differential metrics:

  JS/TS : pilot/smoke-js/reports/mutation.{bdd,nonbdd,full}.json   (Stryker 10.1.1)
  Java  : data/mutants/feasibility-java.{bdd,nonbdd,full}.aligned.csv (PIT 1.30.2)

An important asymmetry, reported rather than hidden:

  * PIT computes coverage in every mode, so `executed(NON_BDD)` is observed and
    S = executed(BDD) & executed(NON_BDD) is exact.
  * Stryker's `command` runner cannot report per-test coverage, so every mutant comes back
    as KILLED or SURVIVED and `executed(NON_BDD)` collapses to "all mutants". S therefore
    collapses to executed(BDD), and the non-BDD kill set is a lower bound. Both effects
    push `DK_bdd_uplift` upward, so the JS figure is an UPPER BOUND and is labelled as
    such. The Java figure is the exact one.

Outputs:
    data/metrics/feasibility.json     machine-readable, consumed by scripts/make_numbers.py
    console table
"""
from __future__ import annotations

import csv
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "analysis"))
from differential import (  # noqa: E402
    INVALID, KILLED, NO_COVERAGE, SURVIVED, TIMEOUT, compute_differential,
)

JS_REPORTS = os.path.join(ROOT, "pilot", "smoke-js", "reports")
JAVA_CSV = os.path.join(ROOT, "data", "mutants")
OUT = os.path.join(ROOT, "data", "metrics", "feasibility.json")

STRYKER_MAP = {
    "Killed": KILLED, "Survived": SURVIVED, "NoCoverage": NO_COVERAGE,
    "Timeout": TIMEOUT, "TimedOut": TIMEOUT, "RuntimeError": INVALID,
    "CompileError": INVALID, "Ignored": INVALID, "Pending": INVALID,
}


def load_stryker(mode: str) -> dict[str, str]:
    path = os.path.join(JS_REPORTS, f"mutation.{mode}.json")
    if not os.path.exists(path):
        return {}
    data = json.load(open(path, encoding="utf-8"))
    out: dict[str, str] = {}
    for fname, fobj in (data.get("files") or {}).items():
        for m in fobj.get("mutants", []):
            mid = str(m.get("id"))
            out[mid] = STRYKER_MAP.get(m.get("status", ""), INVALID)
    return out


def load_pit(mode: str, operators: str = "aligned") -> dict[str, str]:
    path = os.path.join(JAVA_CSV, f"feasibility-java.{mode}.{operators}.csv")
    if not os.path.exists(path):
        return {}
    out: dict[str, str] = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[r["mutant_id"]] = r["status"]
    return out


def counts(st: dict[str, str]) -> dict[str, int]:
    c: dict[str, int] = {}
    for v in st.values():
        c[v] = c.get(v, 0) + 1
    return c


def ms_all_ms_cov(st: dict[str, str]) -> tuple[float | None, float | None]:
    c = counts(st)
    k = c.get(KILLED, 0) + c.get(TIMEOUT, 0)
    s = c.get(SURVIVED, 0)
    t = c.get(TIMEOUT, 0)
    nc = c.get(NO_COVERAGE, 0)
    den_all = k + s + nc
    den_cov = k + s
    return ((k / den_all) if den_all else None), ((k / den_cov) if den_cov else None)


def main() -> int:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    report: dict = {}

    # ---------------- JS / TS (upper bound)
    js = {m: load_stryker(m) for m in ("bdd", "nonbdd", "full")}
    if all(js.values()):
        d = compute_differential(js["bdd"], js["nonbdd"], js["full"])
        ms_all, ms_cov = ms_all_ms_cov(js["bdd"])
        report["js"] = {
            "tool": "Stryker 10.1.1 + @stryker-mutator/cucumber-runner 10.1.1, @cucumber/cucumber 12.2.0",
            "mutants": {m: len(s) for m, s in js.items()},
            "status_counts": {m: counts(s) for m, s in js.items()},
            "bdd_MS_all": ms_all,
            "bdd_MS_cov": ms_cov,
            "no_coverage_control_observed": counts(js["bdd"]).get(NO_COVERAGE, 0),
            "differential": d.as_dict(),
            "bound": "upper bound: Stryker command runner cannot report NON_BDD coverage, "
                     "so S collapses to executed(BDD) and the non-BDD kill set is a lower bound",
        }
        print(f"JS   mutants bdd={len(js['bdd'])} nonbdd={len(js['nonbdd'])} full={len(js['full'])}")
        print(f"JS   BDD MS_all={ms_all:.4f} MS_cov={ms_cov:.4f} NO_COVERAGE={report['js']['no_coverage_control_observed']}")
        print(f"JS   S={d.s_size} DK_bdd_uplift={d.dk_bdd_uplift} (upper bound) "
              f"DK_nonbdd_uplift={d.dk_nonbdd_uplift} BDD_unique={d.bdd_unique_share}")

    # ---------------- Java (exact)
    jv = {m: load_pit(m) for m in ("bdd", "nonbdd", "full")}
    if all(jv.values()):
        d = compute_differential(jv["bdd"], jv["nonbdd"], jv["full"])
        ms_all, ms_cov = ms_all_ms_cov(jv["bdd"])
        report["java"] = {
            "tool": "PIT 1.30.2 + pitest-junit5-plugin 1.2.3, Cucumber-JVM 8.1.0",
            "mutants": {m: len(s) for m, s in jv.items()},
            "status_counts": {m: counts(s) for m, s in jv.items()},
            "bdd_MS_all": ms_all,
            "bdd_MS_cov": ms_cov,
            "no_coverage_control_observed": counts(jv["bdd"]).get(NO_COVERAGE, 0),
            "differential": d.as_dict(),
            "bound": "exact: PIT reports coverage in every mode, so S is the true intersection",
        }
        print(f"JAVA mutants bdd={len(jv['bdd'])} nonbdd={len(jv['nonbdd'])} full={len(jv['full'])}")
        print(f"JAVA BDD MS_all={ms_all:.4f} MS_cov={ms_cov:.4f} NO_COVERAGE={report['java']['no_coverage_control_observed']}")
        print(f"JAVA S={d.s_size} DK_bdd_uplift={d.dk_bdd_uplift} "
              f"DK_nonbdd_uplift={d.dk_nonbdd_uplift} BDD_unique={d.bdd_unique_share}")
    else:
        print("JAVA: incomplete mode set on disk; run pipelines/mutation/feasibility_java.py")

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nwrote {OUT}")
    return 0 if report else 1


if __name__ == "__main__":
    sys.exit(main())
