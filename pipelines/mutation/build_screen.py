#!/usr/bin/env python
"""P2 build/run screen: can a candidate's BDD suite actually execute here?

Eligibility from the static screen is necessary but not sufficient. This stage
attempts a real BDD run per candidate and records the outcome with a CATEGORISED
reason, because build attrition is itself a headline finding of the study
(threat T3: the strongest suites are the likeliest to be unmeasurable).

Funnel states: bdd_passes | build_fails | bdd_fails | timeout | unsupported

Reason vocabulary (fixed):
    dependency_rot, tool_incompatibility, missing_service_dependency,
    needs_browser, needs_database, no_tests_found, compile_error, timeout, other

Output: data/corpus/build_screen.csv (one row per candidate)

Usage:
    python pipelines/mutation/build_screen.py --limit 40
    python pipelines/mutation/build_screen.py --repo owner/name
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REPO_DIR = os.path.join(ROOT, "data", "repos")
OUT = os.path.join(ROOT, "data", "corpus", "build_screen.csv")
JDK = "C:\\Program Files\\Java\\jdk-22"
MVN = os.path.join(ROOT, "tools", "jvm", "maven", "apache-maven-3.9.9", "bin", "mvn.cmd")
GRADLE = os.path.join(ROOT, "tools", "jvm", "gradle", "gradle-8.10.2", "bin", "gradle.bat")
M2 = os.path.join(ROOT, ".m2repo")
GRADLE_HOME = os.path.join(ROOT, ".gradle-home")
NPM_CACHE = os.path.join(ROOT, ".npm-cache")
BUDGET_S = 900
# On Windows npm/npx are .cmd shims; subprocess with shell=False cannot execute the
# extensionless names, which produced spurious instant "build_fails" rows.
NPM = "npm.cmd" if os.name == "nt" else "npm"
NPX = "npx.cmd" if os.name == "nt" else "npx"

FIELDS = ["repo", "language", "state", "reason", "exit_code", "duration_s",
          "runner", "build_dir", "n_tests", "bdd_evidence", "install_ok",
          "install_log", "log_tail", "attempted_utc"]

# A green `mvn test` / `npm test` does NOT prove the BDD suite ran: the project's
# unit tests may have passed while no Cucumber scenario executed at all. The corpus
# is only valid if the Gherkin layer actually runs, so we require positive evidence.
BDD_EVIDENCE_RX = re.compile(
    r"(scenarios?\s*\(|steps?\s*\(|cucumber\.(?:api|runtime)|io\.cucumber|"
    r"@cucumber/cucumber|CucumberOptions|RunWith\s*\(\s*Cucumber|"
    r"cucumber-jvm|cucumber-js|Gherkin|Feature:\s)", re.I)

REASON_PATTERNS = [
    ("needs_browser", re.compile(r"(chromedriver|geckodriver|webdriver|playwright|puppeteer|"
                                 r"browser|selenium|Cannot find (?:chrome|firefox))", re.I)),
    ("missing_service_dependency", re.compile(r"(ECONNREFUSED|connection refused|could not connect|"
                                              r"no such host|localhost:\d+|docker-compose)", re.I)),
    ("needs_database", re.compile(r"(jdbc|datasource|postgres|mysql|mongodb|h2 database|"
                                  r"database connection|flyway|liquibase)", re.I)),
    ("tool_incompatibility", re.compile(r"(Unsupported class file|invalid target release|"
                                        r"release version .* not supported|class file version|"
                                        r"java\.lang\.UnsupportedClassVersionError|"
                                        r"source option \d+ is no longer supported|"
                                        r"requires Java|obsolete)", re.I)),
    ("dependency_rot", re.compile(r"(Could not resolve dependencies|Could not find artifact|"
                                  r"404 Not Found|ETARGET|ERESOLVE|peer dep|"
                                  r"Could not GET|Unable to resolve|no matching version)", re.I)),
    ("compile_error", re.compile(r"(COMPILATION ERROR|error: cannot find symbol|"
                                 r"SyntaxError|TS\d{4}:|error TS)", re.I)),
    ("no_tests_found", re.compile(r"(No tests found|0 scenarios|Nothing to run|"
                                  r"No `@cucumber/cucumber`|no feature files)", re.I)),
    ("timeout", re.compile(r"^(timeout)$", re.I)),
]


def env_for(lang: str) -> dict:
    e = dict(os.environ)
    e["JAVA_HOME"] = JDK
    e["MAVEN_OPTS"] = "-Xmx1500m"
    e["GRADLE_USER_HOME"] = GRADLE_HOME
    e["npm_config_cache"] = NPM_CACHE
    e["CI"] = "true"
    e["GIT_TERMINAL_PROMPT"] = "0"
    e["MAVEN_ARGS"] = f"-Dmaven.repo.local={M2}"
    return e


def run(cmd, cwd, lang, timeout=BUDGET_S):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace", env=env_for(lang), shell=False)
        return p.returncode, (p.stdout or "") + "\n" + (p.stderr or ""), time.time() - t0
    except subprocess.TimeoutExpired as e:
        out = ""
        for s in (e.stdout, e.stderr):
            if s:
                out += s if isinstance(s, str) else s.decode("utf-8", "replace")
        return 124, out + "\ntimeout", time.time() - t0
    except Exception as e:  # noqa: BLE001
        return 1, f"{type(e).__name__}: {e}", time.time() - t0


def classify(code: int, log: str) -> str:
    if code == 124:
        return "timeout"
    for name, rx in REASON_PATTERNS:
        if rx.search(log):
            return name
    return "other"


def count_tests(log: str) -> str:
    m = re.search(r"(\d+)\s+scenarios?\s*\(", log, re.I)
    if m:
        return m.group(1)
    m = re.search(r"Tests run:\s*(\d+)", log)
    if m:
        return m.group(1)
    return ""


def _find_build(d: str, names: tuple[str, ...], max_depth: int = 3) -> str | None:
    """Shallowest build descriptor, searching subdirectories.

    Many BDD repositories are multi-module or keep the buildable project one level
    down (e.g. `example-project/pom.xml`). A root-only check silently mislabels
    them as `unsupported`, which would corrupt the attrition statistics.
    """
    best = None
    root_depth = d.rstrip("\\/").count(os.sep)
    for root, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x not in
                   {".git", "node_modules", "target", "build", "vendor", ".gradle"}]
        depth = root.rstrip("\\/").count(os.sep) - root_depth
        if depth > max_depth:
            dirs[:] = []
            continue
        for n in names:
            if n in files:
                cand = os.path.join(root, n)
                key = (depth, len(cand))
                if best is None or key < best[0]:
                    best = (key, cand)
    return best[1] if best else None


def detect(repo_dir: str) -> tuple[str, list[str], str]:
    """Return (language, command, working-directory-of-the-build)."""
    pom = _find_build(repo_dir, ("pom.xml",))
    pkg = _find_build(repo_dir, ("package.json",))
    grad = _find_build(repo_dir, ("build.gradle", "build.gradle.kts"))

    # Prefer the build file closest to the root; ties go to Maven/Gradle.
    if pom:
        wd = os.path.dirname(pom)
        mvn = os.path.join(wd, "mvnw.cmd")
        base = [mvn] if os.path.isfile(mvn) else [MVN]
        return "java", base + ["-B", "-q", f"-Dmaven.repo.local={M2}", "test"], wd
    if grad:
        wd = os.path.dirname(grad)
        gw = os.path.join(wd, "gradlew.bat")
        base = [gw] if os.path.isfile(gw) else [GRADLE]
        return "java", base + ["test", "--no-daemon", "-q"], wd
    if pkg:
        wd = os.path.dirname(pkg)
        try:
            txt = open(pkg, encoding="utf-8", errors="replace").read()
        except Exception:
            txt = ""
        if re.search(r"@cucumber/cucumber|cucumber-js", txt):
            return "javascript", [NPX, "--no-install", "cucumber-js"], wd
        if re.search(r"playwright", txt) and re.search(r"bdd", txt, re.I):
            return "javascript", [NPX, "--no-install", "playwright", "test"], wd
        return "javascript", [NPM, "test", "--silent"], wd
    if os.path.isfile(os.path.join(repo_dir, "pyproject.toml")) or \
       os.path.isfile(os.path.join(repo_dir, "requirements.txt")):
        return "python", [], repo_dir
    return "unknown", [], repo_dir


def ensure_js_deps(wd: str) -> tuple[bool, str]:
    """Install JS dependencies before running tests.

    Without this, `npm test` fails in ~1 s for every JavaScript candidate because
    node_modules is absent — a harness artifact that would be misread as build
    attrition in the study's attrition statistics. Maven/Gradle resolve their own
    dependencies, so only the JS/TS stratum needs this step.
    """
    if os.path.isdir(os.path.join(wd, "node_modules")):
        return True, "node_modules present"
    pkg = os.path.join(wd, "package.json")
    if not os.path.isfile(pkg):
        return False, "no package.json"
    if os.path.isfile(os.path.join(wd, "pnpm-lock.yaml")):
        cmd = ["pnpm.cmd" if os.name == "nt" else "pnpm", "install", "--silent"]
    elif os.path.isfile(os.path.join(wd, "yarn.lock")):
        cmd = ["yarn.cmd" if os.name == "nt" else "yarn", "install", "--silent"]
    elif os.path.isfile(os.path.join(wd, "package-lock.json")):
        cmd = [NPM, "ci", "--no-audit", "--no-fund", "--silent"]
    else:
        cmd = [NPM, "install", "--no-audit", "--no-fund", "--silent"]
    code, log, dur = run(cmd, wd, "javascript", timeout=1200)
    return code == 0, (" ".join(cmd)) + f" -> exit {code} ({dur:.0f}s)\n" + log[-800:]


def screen_one(repo: str) -> dict:
    from datetime import datetime, timezone
    row = {f: "" for f in FIELDS}
    row["repo"] = repo
    row["attempted_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    d = os.path.join(REPO_DIR, repo.replace("/", "__", 1))
    if not os.path.isdir(d):
        row.update(state="unsupported", reason="other", log_tail="clone missing")
        return row
    lang, cmd, wd = detect(d)
    row["language"] = lang
    row["runner"] = " ".join(cmd) if cmd else ""
    row["build_dir"] = os.path.relpath(wd, d).replace("\\", "/") if wd != d else "."
    if not cmd:
        row.update(state="unsupported", reason="tool_incompatibility",
                   log_tail=f"no supported runner for {lang}")
        return row
    if lang in ("javascript", "typescript"):
        okd, dlog = ensure_js_deps(wd)
        row["install_ok"] = int(okd)
        row["install_log"] = dlog[-600:]
        if not okd:
            row.update(state="build_fails", reason="dependency_rot",
                       log_tail=dlog[-1000:])
            return row
    code, log, dur = run(cmd, wd, lang)
    row["exit_code"] = code
    row["duration_s"] = round(dur, 1)
    row["n_tests"] = count_tests(log)
    tail = "\n".join(log.strip().splitlines()[-12:])[:1200]
    row["log_tail"] = tail
    if code == 0:
        evidence = bool(BDD_EVIDENCE_RX.search(log)) or bool(
            re.search(r"scenarios?\s*\(", log, re.I))
        row["bdd_evidence"] = "yes" if evidence else "no"
        if evidence:
            row["state"] = "bdd_passes"
            row["reason"] = ""
        else:
            # Tests passed but nothing indicates the Gherkin layer executed.
            row["state"] = "no_bdd_execution"
            row["reason"] = "no_tests_found"
    elif code == 124:
        row.update(state="timeout", reason="timeout")
    else:
        reason = classify(code, log)
        # If the runner actually executed tests, the build worked and the SUITE
        # failed; that is `bdd_fails`, not a build failure. Misclassifying it would
        # inflate the build-attrition statistic.
        executed = bool(row["n_tests"]) or bool(
            re.search(r"(Tests run: \d+|scenarios? \(|steps? \(|tests? completed|"
                      r"BUILD FAILURE|Test failures|\d+ failed)", log))
        if reason in ("dependency_rot", "tool_incompatibility", "compile_error", "no_tests_found"):
            state = "build_fails"
        elif executed:
            state = "bdd_fails"
        else:
            state = "build_fails"
        row.update(state=state, reason=reason)
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--repo", default=None)
    ap.add_argument("--candidates", default=os.path.join(ROOT, "data", "corpus", "candidates.csv"))
    ap.add_argument("--out", default=None,
                    help="output CSV; use distinct files when running parallel slices")
    ap.add_argument("--language", default=None,
                    help="restrict to one language (javascript|typescript|java|python)")
    ap.add_argument("--shard", default=None, metavar="K/N",
                    help="process only shard K of N (0-based), for parallel runs")
    a = ap.parse_args()

    global OUT
    if a.out:
        OUT = a.out if os.path.isabs(a.out) else os.path.join(ROOT, a.out)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    done = set()
    if os.path.exists(OUT):
        with open(OUT, newline="", encoding="utf-8") as f:
            done = {r["repo"] for r in csv.DictReader(f)}

    if a.repo:
        targets = [a.repo]
    else:
        if not os.path.exists(a.candidates):
            print(f"build_screen: no candidates file at {a.candidates}")
            return 1
        with open(a.candidates, newline="", encoding="utf-8") as f:
            cand = [r for r in csv.DictReader(f) if r.get("state") == "eligible"]
        if a.language:
            cand = [r for r in cand if (r.get("language") or "") == a.language]
        targets = [r["repo"] for r in cand][: a.limit]
    targets = [t for t in targets if t not in done]
    if a.shard:
        k, n = (int(x) for x in a.shard.split("/"))
        targets = [t for i, t in enumerate(targets) if i % n == k]
    if not targets:
        print("build_screen: nothing to do")
        return 0

    new_file = not os.path.exists(OUT)
    with open(OUT, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        for repo in targets:
            row = screen_one(repo)
            w.writerow(row)
            f.flush()
            print(f"  {row['state']:12s} {row['reason']:28s} {row['duration_s']:>7}s "
                  f"{repo}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
