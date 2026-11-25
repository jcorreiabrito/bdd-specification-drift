#!/usr/bin/env python
"""Three-mode mutation measurement on the Java feasibility suite, via PIT.

PIT is used here rather than Stryker because PIT computes coverage itself in *every*
mode. That matters for the differential: it makes `executed(NON_BDD)` observable, so the
comparison set S = executed(BDD) ∩ executed(NON_BDD) can be computed exactly instead of
being over-approximated (the Stryker `command` runner cannot report coverage, so the JS
harness reports an upper bound on the BDD uplift instead — see the paper's limitations).

Modes:
    bdd     -> PIT targetTests = the JUnit Platform suite that runs the Cucumber features
    nonbdd  -> PIT targetTests = the plain JUnit unit tests
    full    -> PIT targetTests = everything

Operators: `aligned` restricts PIT to decision-logic mutators so the set is comparable
across tools; `default` leaves PIT's own defaults, used only to measure cross-tool
divergence unaligned.

Outputs:
    data/mutants/feasibility-java.<mode>[.<operators>].csv     per-mutant status
    data/metrics/feasibility-java.json                          differential metrics

Usage:
    python pipelines/mutation/feasibility_java.py --operators aligned
    python pipelines/mutation/feasibility_java.py --operators default --mode full
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROJECT = os.path.join(ROOT, "pilot", "smoke-java")
JDK = "C:\\Program Files\\Java\\jdk-22"
MVN = os.path.join(ROOT, "tools", "jvm", "maven", "apache-maven-3.9.9", "bin", "mvn.cmd")
M2 = os.path.join(ROOT, ".m2repo")
OUT_MUT = os.path.join(ROOT, "data", "mutants")
OUT_JSON = os.path.join(ROOT, "data", "metrics", "feasibility-java.json")
PIT_VERSION = "1.30.2"

# Decision-logic operators only: boundaries, negation, arithmetic, constants, returns.
ALIGNED = ",".join([
    "CONDITIONALS_BOUNDARY", "NEGATE_CONDITIONALS", "MATH", "INCREMENTS",
    "INVERT_NEGS", "PRIMITIVE_RETURNS", "EMPTY_RETURNS",
    # PIT 1.30 names these TRUE_RETURNS / FALSE_RETURNS; the older
    # BOOLEAN_TRUE_RETURN / BOOLEAN_FALSE_RETURN names are rejected as unknown.
    "TRUE_RETURNS", "FALSE_RETURNS",
])

TARGET_TESTS = {
    "bdd": "smoke.RunCucumberTest",
    "nonbdd": "smoke.UnitPricingTest",
    "full": "*",
}


def compile_project() -> tuple[int, str]:
    """Compile main and test sources before mutation.

    Invoking `org.pitest:pitest-maven:mutationCoverage` directly by coordinates does NOT
    run the compile phase. On a clean tree that leaves target/classes absent and PIT
    generates zero mutants, which is easily mistaken for "no classes to mutate".
    """
    cmd = [MVN, "-B", "-q", f"-Dmaven.repo.local={M2}", "test-compile"]
    env = dict(os.environ)
    env["JAVA_HOME"] = JDK
    p = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env, timeout=1200)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def run_pit(mode: str, operators: str) -> tuple[int, str, str]:
    report_dir = os.path.join(PROJECT, "target", f"pit-{mode}-{operators}")
    cmd = [
        MVN, "-B", "-q", f"-Dmaven.repo.local={M2}",
        f"org.pitest:pitest-maven:{PIT_VERSION}:mutationCoverage",
        "-DtargetClasses=smoke.pricing.*",
        f"-DtargetTests={TARGET_TESTS[mode]}",
        f"-Dmutators={ALIGNED if operators == 'aligned' else 'DEFAULTS'}",
        "-DoutputFormats=XML",
        "-DtimestampedReports=false",
        f"-DreportsDirectory={report_dir}",
        "-DfailWhenNoMutations=false",
        "-DwithHistory=false",
        "-Dverbose=false",
    ]
    env = dict(os.environ)
    env["JAVA_HOME"] = JDK
    t0 = time.time()
    p = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env, timeout=2400)
    log = (p.stdout or "") + "\n" + (p.stderr or "")
    print(f"  pit {mode}/{operators}: exit={p.returncode} in {time.time()-t0:.0f}s")
    return p.returncode, log, os.path.join(report_dir, "mutations.xml")


def parse_pit_xml(path: str) -> dict[str, str]:
    """mutant_id -> normalised status."""
    out: dict[str, str] = {}
    if not os.path.exists(path):
        return out
    root = ET.parse(path).getroot()
    for m in root.iter("mutation"):
        detected = m.get("detected") == "true"
        status_txt = (m.get("status") or "").upper()
        if status_txt in ("NO_COVERAGE", "NOT_STARTED"):
            st = "NO_COVERAGE"
        elif status_txt in ("TIMED_OUT", "TIMEOUT", "MEMORY_ERROR"):
            st = "TIMEOUT"
        elif status_txt in ("RUN_ERROR", "NON_VIABLE", "COMPILE_ERROR"):
            st = "INVALID"
        elif status_txt == "KILLED" or detected:
            st = "KILLED"
        else:
            st = "SURVIVED"
        key = "|".join([
            m.findtext("mutatedClass", ""), m.findtext("mutatedMethod", ""),
            m.findtext("lineNumber", ""), m.findtext("mutator", ""),
            m.findtext("description", ""),
        ])
        out[key] = st
    return out


def write_csv(path: str, statuses: dict[str, str], mode: str, operators: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["repo", "language", "mode", "mutant_id", "status"])
        for i, (k, st) in enumerate(sorted(statuses.items())):
            w.writerow(["feasibility-java", "java", f"{mode}/{operators}", f"j{i:04d}", st])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--operators", default="aligned", choices=["aligned", "default"])
    ap.add_argument("--mode", default=None, choices=["bdd", "nonbdd", "full"])
    a = ap.parse_args()

    modes = [a.mode] if a.mode else ["bdd", "nonbdd", "full"]
    os.makedirs(OUT_MUT, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)

    code, clog = compile_project()
    print(f"  compile: exit={code}")
    if code != 0:
        print("\n".join(l[:200] for l in clog.strip().splitlines()[-15:]))
        return 1

    collected: dict[str, dict[str, str]] = {}
    for mode in modes:
        code, log, xml = run_pit(mode, a.operators)
        st = parse_pit_xml(xml)
        collected[mode] = st
        write_csv(os.path.join(OUT_MUT, f"feasibility-java.{mode}.{a.operators}.csv"),
                  st, mode, a.operators)
        counts: dict[str, int] = {}
        for v in st.values():
            counts[v] = counts.get(v, 0) + 1
        print(f"  {mode:7s} mutants={len(st):4d} {counts}")
        if not st:
            print(f"  PIT produced no mutants for {mode}; log tail:")
            print("\n".join(l[:200] for l in log.strip().splitlines()[-12:]))

    # Differential only when all three modes are present in this invocation.
    result = {"suite": "feasibility-java", "operators": a.operators,
              "modes": {m: len(s) for m, s in collected.items()}}
    if all(m in collected and collected[m] for m in ("bdd", "nonbdd", "full")):
        sys.path.insert(0, os.path.join(ROOT, "pipelines", "analysis"))
        from differential import compute_differential
        d = compute_differential(collected["bdd"], collected["nonbdd"], collected["full"])
        result["differential"] = d.as_dict()
        print("\n=== three-mode differential (PIT, coverage observable in all modes) ===")
        for k, v in d.as_dict().items():
            print(f"  {k:22s} {v}")
    else:
        print("\n(incomplete mode set in this invocation; differential not computed)")

    # Merge into the shared JSON so separate invocations accumulate.
    merged = {}
    if os.path.exists(OUT_JSON):
        try:
            merged = json.load(open(OUT_JSON, encoding="utf-8"))
        except Exception:
            merged = {}
    merged[f"{a.operators}"] = result
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)
    print(f"\nwrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
