#!/usr/bin/env python
"""P2 corpus screener (frame v2) — licence + APPLICATION SHAPE + BDD runner.

Why v2 exists: the P1.5 pilot (170 repos, 5.3% eligible) showed the frame is
dominated by BDD *tooling* repositories — reporting agents, test utilities, Maven
plugins. Those pass a naive `*.feature` + build + licence test but have **no domain
layer**, which the whole "mutants proxy business-rule change" construct requires.
Frame v2 adds an application-shape test and a BDD-runner-in-manifest test, as
approved at the gate (decision D2).

Eligibility (v2), all must hold:
  E1  >= 1 .feature file
  E2  >= 20 scenarios (Scenario | Scenario Outline | Cenário | Cenário Esquema)
  E3  >= 1 step-definition file
  E4  >= 1 build descriptor (pom.xml, build.gradle, package.json, pyproject, ...)
  E5  permissive licence detected
  E6  language in {java, javascript, typescript, python}  (.NET out of protocol)
  E7  APPLICATION SHAPE: >= 10 non-test source files in a main source tree
  E8  BDD runner named in a build manifest / lockfile / dependency file

Every repository gets exactly one funnel state and a categorised reason.

Usage:
    python scripts/corpus_screen.py --limit 700
    python scripts/corpus_screen.py --limit 700 --resume
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
from collections import Counter

SEED = 20261125
FRAME = os.path.join("data", "frame", "frame_repos.csv")
PILOT = os.path.join("data", "pilot", "screen.csv")
OUT_DIR = os.path.join("data", "corpus")
REPO_DIR = os.path.join("data", "repos")
OUT = os.path.join(OUT_DIR, "candidates.csv")
CLONE_TIMEOUT = 240

MIN_SCENARIOS = 20
MIN_APP_SOURCES = 10

PERMISSIVE = ("mit", "apache", "bsd", "isc", "mpl", "lgpl", "gpl", "epl",
              "unlicense", "cc0", "cc-by", "artistic", "zlib")

BUILD_FILES = {"pom.xml", "build.gradle", "build.gradle.kts", "package.json",
               "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt",
               "build.sbt", "build.xml", "gradlew", "mvnw"}

SCENARIO_RX = re.compile(
    r"^\s*(Scenario|Scenario Outline|Scenario Template|Cenário|Cenário Esquema|Ejemplo)\s*:", re.M)

STEP_RX = [
    re.compile(r"@(?:Given|When|Then|And|But)\s*\("),
    re.compile(r"\[\s*(?:Given|When|Then|And|But)\s*\("),
    re.compile(r"^\s*(?:Given|When|Then|And|But)\s*[({\"']", re.M),
    re.compile(r"func\s+.*\*\w+Step"),          # godog
]

BDD_DEP_RX = re.compile(
    r"(cucumber|behave|pytest[-_]bdd|playwright[-_]bdd|serenity|karate|specflow|reqnroll|gherkin)",
    re.I)

TEST_PATH_RX = re.compile(
    r"(^|[\\/])(test|tests|spec|specs|__tests__|e2e|acceptance|integration[-_]?test[s]?|features?)([\\/]|$)",
    re.I)
TEST_FILE_RX = re.compile(
    r"(Test|Tests|IT|Spec)\.(java|kt|groovy)$|_test\.py$|^test_.*\.py$|\.(test|spec)\.(js|jsx|ts|tsx)$",
    re.I)

LANG_BY_EXT = {".java": "java", ".kt": "java", ".groovy": "java",
               ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript",
               ".cjs": "javascript", ".ts": "typescript", ".tsx": "typescript",
               ".py": "python"}

FIELDS = ["repo", "state", "reason", "language", "licence", "n_features",
          "n_scenarios", "n_step_files", "n_app_sources", "n_test_sources",
          "build_files", "bdd_runner", "last_commit", "n_files", "notes"]


def run(cmd, cwd=None, timeout=CLONE_TIMEOUT):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout, encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "timeout"
    except Exception as e:  # noqa: BLE001
        return 1, f"{type(e).__name__}: {e}"


def licence_of(path):
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "LICENCE", "LICENSE.rst"):
        p = os.path.join(path, name)
        if os.path.isfile(p):
            try:
                head = open(p, encoding="utf-8", errors="replace").read(6000).lower()
            except Exception:
                return "unreadable"
            for k in PERMISSIVE:
                if k in head:
                    return k
            return "other"
    for manifest in ("package.json", "pyproject.toml", "pom.xml", "setup.py"):
        p = os.path.join(path, manifest)
        if os.path.isfile(p):
            try:
                txt = open(p, encoding="utf-8", errors="replace").read(20000)
            except Exception:
                continue
            m = re.search(r'"license"\s*:\s*"([^"]+)"', txt) or \
                re.search(r"license\s*=\s*[\"']([^\"']+)", txt) or \
                re.search(r"<license>.*?<name>([^<]+)</name>", txt, re.S)
            if m:
                return m.group(1).lower().strip()
    return "none_found"


def screen(slug: str) -> dict:
    owner, name = slug.split("/", 1)
    dest = os.path.join(REPO_DIR, f"{owner}__{name}")
    row = {f: "" for f in FIELDS}
    row.update(repo=slug, n_features=0, n_scenarios=0, n_step_files=0,
               n_app_sources=0, n_test_sources=0, n_files=0)

    if not os.path.isdir(dest):
        code, out = run(["git", "clone", "--depth", "1", "--quiet",
                         f"https://github.com/{slug}.git", dest])
        if code != 0:
            row.update(state="excluded", reason="clone_failed", notes=out.strip()[:150])
            return row
    row["state"] = "cloned"

    code, lastc = run(["git", "log", "-1", "--format=%cI"], cwd=dest, timeout=60)
    row["last_commit"] = lastc.strip()[:19] if code == 0 else ""

    features = 0
    scenarios = 0
    step_files = 0
    app_src = 0
    test_src = 0
    n_files = 0
    builds: list[str] = []
    manifests: list[str] = []
    lang_votes: Counter = Counter()

    for root, dirs, files in os.walk(dest):
        dirs[:] = [d for d in dirs if d not in
                   {".git", "node_modules", "target", "build", "vendor", "dist",
                    ".gradle", "__pycache__", ".venv", "venv"}]
        rel_root = os.path.relpath(root, dest)
        for fn in files:
            n_files += 1
            low = fn.lower()
            path = os.path.join(root, fn)
            ext = os.path.splitext(low)[1]
            if low in BUILD_FILES:
                builds.append(os.path.join(rel_root, fn).replace("\\", "/"))
                manifests.append(path)
            if low.endswith(".feature"):
                features += 1
                try:
                    scenarios += len(SCENARIO_RX.findall(
                        open(path, encoding="utf-8", errors="replace").read()))
                except Exception:
                    pass
                continue
            if ext in LANG_BY_EXT:
                try:
                    head = open(path, encoding="utf-8", errors="replace").read(20000)
                except Exception:
                    head = ""
                if any(p.search(head) for p in STEP_RX):
                    step_files += 1
                is_test = bool(TEST_FILE_RX.search(fn)) or bool(TEST_PATH_RX.search(rel_root))
                if is_test:
                    test_src += 1
                else:
                    app_src += 1
                    lang_votes[LANG_BY_EXT[ext]] += 1

    bdd_runner = ""
    for m in manifests:
        try:
            txt = open(m, encoding="utf-8", errors="replace").read(200000)
        except Exception:
            continue
        hit = BDD_DEP_RX.search(txt)
        if hit:
            bdd_runner = hit.group(1).lower()
            break

    row.update(n_features=features, n_scenarios=scenarios, n_step_files=step_files,
               n_app_sources=app_src, n_test_sources=test_src, n_files=n_files,
               build_files=";".join(sorted(builds)[:4]), bdd_runner=bdd_runner,
               licence=licence_of(dest),
               language=(lang_votes.most_common(1)[0][0] if lang_votes else "unknown"))

    # --- eligibility, ordered so the reason is the most fundamental blocker ---
    if features == 0:
        row.update(state="excluded", reason="no_feature_files")
    elif scenarios < MIN_SCENARIOS:
        row.update(state="excluded", reason="too_few_scenarios")
    elif step_files == 0:
        row.update(state="excluded", reason="no_step_definitions")
    elif not builds:
        row.update(state="excluded", reason="no_build_config")
    elif row["language"] not in ("java", "javascript", "typescript", "python"):
        row.update(state="excluded", reason="language_out_of_scope")
    elif not any(k in row["licence"] for k in PERMISSIVE):
        row.update(state="excluded", reason="licence_not_permissive")
    elif not bdd_runner:
        row.update(state="excluded", reason="no_bdd_runner_dependency")
    elif app_src < MIN_APP_SOURCES:
        row.update(state="excluded", reason="no_application_shape")
    else:
        row.update(state="eligible", reason="")
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=700)
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(REPO_DIR, exist_ok=True)

    with open(FRAME, newline="", encoding="utf-8") as f:
        repos = [r["repo"] for r in csv.DictReader(f)]

    prior: dict[str, dict] = {}
    prior_src = OUT if a.resume and os.path.exists(OUT) else (PILOT if os.path.exists(PILOT) else None)
    if prior_src:
        with open(prior_src, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                prior[r["repo"]] = r

    ordered = sorted(repos, key=lambda r: hashlib.sha256(f"{SEED}:{r}".encode()).hexdigest())
    rows: list[dict] = []
    eligible = 0
    reused = 0

    for slug in ordered[: a.limit + len(prior)]:
        if slug in prior:
            # Reuse earlier screening only when it already recorded the v2 fields.
            p = prior[slug]
            if "n_app_sources" in p and p.get("n_app_sources") not in (None, ""):
                rows.append({k: p.get(k, "") for k in FIELDS})
                reused += 1
                if p.get("state") == "eligible":
                    eligible += 1
                continue
        row = screen(slug)
        rows.append(row)
        if row["state"] == "eligible":
            eligible += 1
        else:
            shutil.rmtree(os.path.join(REPO_DIR, slug.replace("/", "__", 1)), ignore_errors=True)
        if len(rows) % 25 == 0:
            print(f"  ... {len(rows)} screened, {eligible} eligible", flush=True)
        if len(rows) >= a.limit:
            break

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    states = Counter(r["state"] for r in rows)
    reasons = Counter(r["reason"] for r in rows if r["reason"])
    langs = Counter(r["language"] for r in rows if r["state"] == "eligible")
    n = len(rows)
    k = states.get("eligible", 0)

    def wilson(kk, nn, z=1.959963985):
        if nn == 0:
            return (0.0, 1.0)
        p = kk / nn
        d = 1 + z * z / nn
        c = (p + z * z / (2 * nn)) / d
        h = z * ((p * (1 - p) / nn + z * z / (4 * nn * nn)) ** 0.5) / d
        return (max(0.0, c - h), min(1.0, c + h))

    lo, hi = wilson(k, n)
    summary = {
        "screened": n, "reused_from_pilot": reused, "eligible": k,
        "yield_pct": round(100.0 * k / max(n, 1), 2),
        "wilson_lo_pct": round(100.0 * lo, 2), "wilson_hi_pct": round(100.0 * hi, 2),
        "frame_size": len(repos), "seed": SEED,
        "reasons": dict(reasons.most_common()),
        "eligible_by_language": dict(langs),
    }
    with open(os.path.join(OUT_DIR, "SCREENING.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
