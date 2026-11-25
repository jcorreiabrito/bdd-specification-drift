#!/usr/bin/env python
"""Mutation measurement: per-mutant status for BDD-only and full-suite modes.

Implements docs/method.md section 8 at the level the environment supports.

Supported paths
---------------
* Java + Maven -> PIT invoked **by plugin coordinates**, so the target repository's
  pom.xml does not have to be edited. Gradle projects without a pre-configured PIT
  task are recorded as `tool_incompatibility`, not silently skipped.
* JS/TS -> Stryker. For the BDD-only mode the official cucumber runner is used
  (proven in results/RUNLOG.md R001); for the full-suite mode Stryker's `command`
  runner executes the project's own `npm test`.

Why full mode needs no coverage analysis
---------------------------------------
The protocol defines S = mutants executed in BOTH modes, and asserts
executed(bdd) subset-of executed(full). So S is obtained from the BDD run's
per-mutant coverage, and every mutant in S is by containment executed by the full
suite. `MS_cov_full(S)` is therefore computable from kill/survive status alone.

Output: data/mutants/<owner>__<name>.<mode>.csv  (one row per mutant)
        columns: mutant_id,status,file,line,mutator,language,mode,repo

Status vocabulary (normalised, protocol 7.1):
    KILLED | SURVIVED | NO_COVERAGE | TIMEOUT | INVALID

Usage:
    python pipelines/mutation/measure.py --repo owner/name --mode bdd
    python pipelines/mutation/measure.py --repo owner/name --mode full
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REPO_DIR = os.path.join(ROOT, "data", "repos")
OUT_DIR = os.path.join(ROOT, "data", "mutants")
JDK = "C:\\Program Files\\Java\\jdk-22"
MVN = os.path.join(ROOT, "tools", "jvm", "maven", "apache-maven-3.9.9", "bin", "mvn.cmd")
M2 = os.path.join(ROOT, ".m2repo")
NPM_CACHE = os.path.join(ROOT, ".npm-cache")
PIT_VERSION = "1.30.2"
PIT_JUNIT5 = "1.2.3"
CUCUMBER_RUNNER_VERSION = "10.1.1"
STRYKER_VERSION = "10.1.1"
BUDGET_S = 3600

# PIT mutator groups aligned to decision logic (protocol section 8).
PIT_MUTATORS = ",".join([
    "CONDITIONALS_BOUNDARY", "NEGATE_CONDITIONALS", "MATH", "INCREMENTS",
    "INVERT_NEGS", "RETURN_VALS", "PRIMITIVE_RETURNS", "BOOLEAN_TRUE_RETURN",
    "BOOLEAN_FALSE_RETURN", "EMPTY_RETURNS", "VOID_METHOD_CALLS",
])


def env() -> dict:
    e = dict(os.environ)
    e["JAVA_HOME"] = JDK
    e["MAVEN_OPTS"] = "-Xmx1500m"
    e["npm_config_cache"] = NPM_CACHE
    e["CI"] = "true"
    e["GIT_TERMINAL_PROMPT"] = "0"
    return e


def run(cmd, cwd, timeout=BUDGET_S):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace", env=env())
        return p.returncode, (p.stdout or "") + "\n" + (p.stderr or ""), time.time() - t0
    except subprocess.TimeoutExpired as e:
        out = ""
        for s in (e.stdout, e.stderr):
            if s:
                out += s if isinstance(s, str) else s.decode("utf-8", "replace")
        return 124, out + "\ntimeout", time.time() - t0
    except Exception as e:  # noqa: BLE001
        return 1, f"{type(e).__name__}: {e}", time.time() - t0


def slug(repo: str) -> str:
    return repo.replace("/", "__", 1)


def load_domain_files(repo: str) -> list[str]:
    """Domain set from the static metrics stage (protocol 7.5)."""
    p = os.path.join(ROOT, "data", "metrics", "static_indicators.csv")
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["repo"] == repo:
                return [x for x in (r.get("domain_files") or "").split(";") if x]
    return []


# --------------------------------------------------------------------- Java/PIT

def java_packages(domain_files: list[str]) -> list[str]:
    pkgs = set()
    for rel in domain_files:
        m = re.search(r"src/main/java/(.+)/[^/]+\.java$", rel.replace("\\", "/"))
        if m:
            pkgs.add(m.group(1).replace("/", "."))
    return sorted(pkgs)


def find_bdd_test_class(repo_dir: str) -> str | None:
    """Locate the JUnit Platform suite that runs the Cucumber features."""
    best = None
    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if d not in {".git", "target", "build", "node_modules"}]
        for fn in files:
            if not fn.endswith((".java", ".kt")):
                continue
            p = os.path.join(root, fn)
            try:
                src = open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            if re.search(r'@IncludeEngines\s*\(\s*"cucumber"\s*\)', src) or \
               re.search(r"@RunWith\s*\(\s*Cucumber\.class\s*\)", src) or \
               re.search(r"@CucumberOptions", src):
                rel = os.path.relpath(p, repo_dir)
                m = re.search(r"(?:src/test/java|src/test/kotlin)/(.+)\.(?:java|kt)$", rel.replace("\\", "/"))
                if m:
                    best = m.group(1).replace("/", ".")
                    return best
    return best


def measure_java(repo: str, mode: str) -> tuple[int, str, list[dict]]:
    d = os.path.join(REPO_DIR, slug(repo))
    domain = load_domain_files(repo)
    pkgs = java_packages(domain)
    if not pkgs:
        return 1, "no domain packages resolvable to src/main/java", []
    target_classes = ",".join(p + ".*" for p in pkgs)
    if mode == "bdd":
        tc = find_bdd_test_class(d)
        if not tc:
            return 1, "no Cucumber JUnit-platform suite class found", []
        target_tests = tc
    else:
        target_tests = "*"

    report_dir = os.path.join(d, "target", "pit-reports-" + mode)
    cmd = [MVN, "-B", "-q", f"-Dmaven.repo.local={M2}",
           f"org.pitest:pitest-maven:{PIT_VERSION}:mutationCoverage",
           f"-DtargetClasses={target_classes}",
           f"-DtargetTests={target_tests}",
           f"-Dmutators={PIT_MUTATORS}",
           f"-DoutputFormats=XML",
           "-DtimestampedReports=false",
           f"-DreportsDirectory={report_dir}",
           "-DfailWhenNoMutations=false",
           "-DwithHistory=false",
           f"-DjvmArgs=-Xmx1200m",
           "-Dverbose=false"]
    try:
        plugin_cp = f"org.pitest:pitest-junit5-plugin:{PIT_JUNIT5}"
        cmd.append(f"-DpluginDependency={plugin_cp}")
    except Exception:
        pass
    code, log, dur = run(cmd, d)
    xml_path = os.path.join(report_dir, "mutations.xml")
    rows: list[dict] = []
    if os.path.exists(xml_path):
        rows = parse_pit_xml(xml_path, repo, mode)
    return code, log, rows


def parse_pit_xml(path: str, repo: str, mode: str) -> list[dict]:
    rows = []
    try:
        tree = ET.parse(path)
    except Exception:
        return rows
    for m in tree.getroot().iter("mutation"):
        detected = m.get("detected")
        status_txt = (m.get("status") or "").upper()
        if status_txt in ("KILLED",) or detected == "true":
            st = "KILLED"
        elif status_txt in ("NO_COVERAGE", "NOT_STARTED"):
            st = "NO_COVERAGE"
        elif status_txt in ("TIMED_OUT", "TIMEOUT", "MEMORY_ERROR"):
            st = "TIMEOUT"
        elif status_txt in ("RUN_ERROR", "NON_VIABLE", "COMPILE_ERROR"):
            st = "INVALID"
        elif status_txt in ("SURVIVED",):
            st = "SURVIVED"
        else:
            st = "SURVIVED" if detected == "false" else "INVALID"
        key = "|".join([
            m.findtext("mutatedClass", ""), m.findtext("mutatedMethod", ""),
            m.findtext("lineNumber", ""), m.findtext("mutator", ""),
            m.findtext("description", ""),
        ])
        rows.append({
            "repo": repo, "language": "java", "mode": mode,
            "mutant_id": hashlib.sha1(key.encode()).hexdigest()[:16],
            "status": st,
            "file": m.findtext("sourceFile", ""),
            "line": m.findtext("lineNumber", ""),
            "mutator": m.findtext("mutator", ""),
        })
    return rows


# ------------------------------------------------------------------- JS/Stryker

def ensure_stryker(d: str) -> tuple[bool, str]:
    if os.path.isdir(os.path.join(d, "node_modules", "@stryker-mutator", "core")) and \
       os.path.isdir(os.path.join(d, "node_modules", "@stryker-mutator", "cucumber-runner")):
        return True, ""
    code, log, _ = run(["npm", "install", "--no-save", "--no-audit", "--no-fund",
                        f"@stryker-mutator/core@{STRYKER_VERSION}",
                        f"@stryker-mutator/cucumber-runner@{CUCUMBER_RUNNER_VERSION}"], d, timeout=1200)
    ok = code == 0
    return ok, log[-1500:]


MUTATOR_MAP = {
    "EqualityOperator": "CONDITIONALS_BOUNDARY",
    "ConditionalExpression": "NEGATE_CONDITIONALS",
    "ArithmeticOperator": "MATH",
    "StringLiteral": "RETURN_VALS",
    "BooleanLiteral": "BOOLEAN_RETURN",
    "BlockStatement": "VOID_METHOD_CALLS",
    "UnaryOperator": "INVERT_NEGS",
    "UpdateOperator": "INCREMENTS",
    "ArrayDeclaration": "RETURN_VALS",
    "OptionalChaining": "NEGATE_CONDITIONALS",
    "LogicalOperator": "NEGATE_CONDITIONALS",
}


def measure_js(repo: str, mode: str) -> tuple[int, str, list[dict]]:
    d = os.path.join(REPO_DIR, slug(repo))
    domain = load_domain_files(repo)
    if not domain:
        return 1, "no domain files from static metrics", []
    ok, log = ensure_stryker(d)
    if not ok:
        return 1, "stryker install failed: " + log, []

    mutate = [x for x in domain]
    cfg_name = f"stryker.tmp.{mode}.json"
    if mode == "bdd":
        features = []
        for root, dirs, files in os.walk(d):
            dirs[:] = [x for x in dirs if x not in {".git", "node_modules", "target", "build"}]
            for fn in files:
                if fn.endswith(".feature"):
                    features.append(os.path.relpath(os.path.join(root, fn), d).replace("\\", "/"))
        if not features:
            return 1, "no .feature files for cucumber runner", []
        cfg = {
            "testRunner": "cucumber",
            "cucumber": {"features": features[:200]},
            "mutate": mutate,
            "coverageAnalysis": "perTest",
            "reporters": ["json"],
            "jsonReporter": {"fileName": f"reports/mutation.{mode}.json"},
            "timeoutMS": 30000,
            "concurrency": 2,
            "thresholds": {"high": 100, "low": 0},
        }
    else:
        pkg = {}
        try:
            pkg = json.load(open(os.path.join(d, "package.json"), encoding="utf-8"))
        except Exception:
            pass
        test_cmd = (pkg.get("scripts") or {}).get("test")
        if not test_cmd:
            return 1, "no npm test script: full-suite mode unavailable", []
        cfg = {
            "testRunner": "command",
            "commandRunner": {"command": "npm test"},
            "mutate": mutate,
            "coverageAnalysis": "off",
            "reporters": ["json"],
            "jsonReporter": {"fileName": f"reports/mutation.{mode}.json"},
            "timeoutMS": 30000,
            "concurrency": 2,
            "thresholds": {"high": 100, "low": 0},
        }
    cfg_path = os.path.join(d, cfg_name)
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    try:
        code, log, dur = run(["npx", "--no-install", "stryker", "run", cfg_name], d)
        rep = os.path.join(d, "reports", f"mutation.{mode}.json")
        rows = parse_stryker_json(rep, repo, mode) if os.path.exists(rep) else []
        return code, log, rows
    finally:
        try:
            os.remove(cfg_path)
        except Exception:
            pass


def parse_stryker_json(path: str, repo: str, mode: str) -> list[dict]:
    rows = []
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception:
        return rows
    for fname, fobj in (data.get("files") or {}).items():
        for m in fobj.get("mutants", []):
            st = (m.get("status") or "").upper()
            mapping = {
                "KILLED": "KILLED", "SURVIVED": "SURVIVED", "NO_COVERAGE": "NO_COVERAGE",
                "TIMEOUT": "TIMEOUT", "TIMEDOUT": "TIMEOUT", "RUNTIMEERROR": "INVALID",
                "COMPILEERROR": "INVALID", "IGNORED": "INVALID", "PENDING": "INVALID",
            }
            status = mapping.get(st, "INVALID")
            loc = (m.get("location") or {}).get("start") or {}
            key = "|".join([fname, str(loc.get("line")), str(loc.get("column")),
                            m.get("mutatorName", ""), m.get("replacement", "")])
            rows.append({
                "repo": repo, "language": "javascript", "mode": mode,
                "mutant_id": hashlib.sha1(key.encode()).hexdigest()[:16],
                "status": status,
                "file": fname,
                "line": loc.get("line", ""),
                "mutator": m.get("mutatorName", ""),
            })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--mode", required=True, choices=["bdd", "full"])
    ap.add_argument("--language", default=None)
    a = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    d = os.path.join(REPO_DIR, slug(a.repo))
    lang = a.language
    if lang is None:
        if os.path.isfile(os.path.join(d, "pom.xml")):
            lang = "java"
        elif os.path.isfile(os.path.join(d, "package.json")):
            lang = "javascript"
        else:
            lang = "unknown"

    if lang == "java":
        code, log, rows = measure_java(a.repo, a.mode)
    elif lang in ("javascript", "typescript"):
        code, log, rows = measure_js(a.repo, a.mode)
    else:
        print(json.dumps({"repo": a.repo, "mode": a.mode, "error": "unsupported language"}))
        return 1

    out = os.path.join(OUT_DIR, f"{slug(a.repo)}.{a.mode}.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["repo", "language", "mode", "mutant_id",
                                          "status", "file", "line", "mutator"])
        w.writeheader()
        w.writerows(rows)

    from collections import Counter
    summary = {
        "repo": a.repo, "mode": a.mode, "language": lang, "exit_code": code,
        "mutants": len(rows),
        "status_counts": dict(Counter(r["status"] for r in rows)),
        "out": out,
        "log_tail": "\n".join(log.strip().splitlines()[-10:])[:1500],
    }
    print(json.dumps(summary, indent=2))
    return 0 if rows else 1


if __name__ == "__main__":
    sys.exit(main())
