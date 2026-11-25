#!/usr/bin/env python
"""P1.5 pilot: draw a seeded stratified sample from the frame, clone, screen eligibility.

This produces the ATTRITION DATA for the gate. Every repository is recorded in
exactly one funnel state with a CATEGORISED reason. Nothing is silently dropped.

Funnel states:
    selected      - drawn from the frame
    cloned        - shallow clone succeeded
    excluded      - fails an eligibility rule (reason categorised)
    eligible      - passes all static eligibility checks
    build_pending - eligible, awaiting the build/mutation attempt

Exclusion reason categories (fixed vocabulary, from the protocol):
    no_feature_files, too_few_scenarios, no_step_definitions,
    no_build_config, licence_not_permissive, no_domain_layer,
    clone_failed, archived_or_empty, other

Draw method: hash-ordered permutation, SHA-256("<seed>:<repo>"). This is
reproducible in any language and does not depend on Python's RNG implementation.

Outputs:
    data/pilot/screen.csv     one row per selected repository
    data/pilot/PILOT.md       yield summary
"""
from __future__ import annotations

import csv
import hashlib
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict

SEED = 20261125
FRAME = os.path.join("data", "frame", "frame_repos.csv")
OUT_DIR = os.path.join("data", "pilot")
REPO_DIR = os.path.join("data", "repos")
MAX_SCREEN = 170         # how many to attempt before stopping
TARGET_ELIGIBLE = 40     # do not stop early: we need a yield estimate with a CI
MIN_SCENARIOS = 20       # protocol eligibility rule
CLONE_TIMEOUT = 180

PERMISSIVE = (
    "mit", "apache", "bsd", "isc", "mpl", "lgpl", "gpl", "epl", "unlicense",
    "cc0", "cc-by", "artistic", "zlib",
)

BUILD_FILES = ["pom.xml", "build.gradle", "build.gradle.kts", "package.json",
               "pyproject.toml", "setup.py", "requirements.txt", "build.sbt",
               "build.xml", "gradlew", "mvnw"]
# .NET / other ecosystems use extension-based build descriptors.
BUILD_EXTS = (".csproj", ".fsproj", ".vbproj", ".sln")

STEP_PATTERNS = [
    re.compile(r"@Given\s*\("), re.compile(r"@When\s*\("), re.compile(r"@Then\s*\("),
    re.compile(r"\[Given\s*\("), re.compile(r"\[When\s*\("), re.compile(r"\[Then\s*\("),
    re.compile(r"^\s*Given\s*\(", re.M), re.compile(r"^\s*When\s*\(", re.M),
    re.compile(r"^\s*Then\s*\(", re.M),
]

SCENARIO_RX = re.compile(r"^\s*(Scenario|Scenario Outline|Cenário|Cenário Esquema)\s*:", re.M)


def run(cmd: list[str], cwd: str | None = None, timeout: int = CLONE_TIMEOUT) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout, encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "timeout"
    except Exception as e:  # noqa: BLE001
        return 1, f"{type(e).__name__}: {e}"


def licence_of(repo_path: str) -> str:
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "LICENCE"):
        p = os.path.join(repo_path, name)
        if os.path.isfile(p):
            try:
                head = open(p, encoding="utf-8", errors="replace").read(4000).lower()
            except Exception:
                return "unreadable"
            for key in PERMISSIVE:
                if key in head:
                    return key
            return "other:" + re.sub(r"\s+", " ", head[:60])
    # package.json / pom.xml licence fields
    pj = os.path.join(repo_path, "package.json")
    if os.path.isfile(pj):
        try:
            txt = open(pj, encoding="utf-8", errors="replace").read()
            m = re.search(r'"license"\s*:\s*"([^"]+)"', txt)
            if m:
                return m.group(1).lower()
        except Exception:
            pass
    return "none_found"


def screen(slug: str) -> dict:
    owner, name = slug.split("/", 1)
    dest = os.path.join(REPO_DIR, f"{owner}__{name}")
    row = {"repo": slug, "state": "", "reason": "", "licence": "", "n_features": 0,
           "n_scenarios": 0, "has_steps": "", "build_files": "", "n_files": 0,
           "last_commit": "", "notes": ""}

    if not os.path.isdir(dest):
        code, out = run(["git", "clone", "--depth", "1", "--quiet",
                         f"https://github.com/{slug}.git", dest])
        if code != 0:
            row.update(state="excluded", reason="clone_failed", notes=out.strip()[:160])
            return row
    row["state"] = "cloned"

    code, lastc = run(["git", "log", "-1", "--format=%cI"], cwd=dest, timeout=60)
    row["last_commit"] = lastc.strip()[:19] if code == 0 else ""

    features, scenarios, stepfiles = [], 0, 0
    n_files = 0
    build_hits: list[str] = []
    for root, dirs, files in os.walk(dest):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "target", "build", "vendor", "dist"}]
        for fn in files:
            n_files += 1
            low = fn.lower()
            path = os.path.join(root, fn)
            if low in BUILD_FILES or low.endswith(BUILD_EXTS):
                rel = os.path.relpath(path, dest).replace("\\", "/")
                build_hits.append(rel)
            if low.endswith(".feature"):
                features.append(path)
                try:
                    txt = open(path, encoding="utf-8", errors="replace").read()
                    scenarios += len(SCENARIO_RX.findall(txt))
                except Exception:
                    pass
            elif low.endswith((".java", ".js", ".ts", ".py", ".rb", ".cs", ".kt", ".groovy")):
                try:
                    txt = open(path, encoding="utf-8", errors="replace").read(20000)
                    if any(p.search(txt) for p in STEP_PATTERNS):
                        stepfiles += 1
                except Exception:
                    pass

    row["n_features"] = len(features)
    row["n_scenarios"] = scenarios
    row["has_steps"] = "yes" if stepfiles else "no"
    row["n_files"] = n_files
    row["licence"] = licence_of(dest)
    # Recursive: multi-module and monorepo layouts keep the build file below the root.
    row["build_files"] = ";".join(sorted(build_hits)[:4])

    if not features:
        row.update(state="excluded", reason="no_feature_files")
    elif scenarios < MIN_SCENARIOS:
        row.update(state="excluded", reason="too_few_scenarios")
    elif not stepfiles:
        row.update(state="excluded", reason="no_step_definitions")
    elif not row["build_files"]:
        row.update(state="excluded", reason="no_build_config")
    elif not any(k in row["licence"] for k in PERMISSIVE):
        row.update(state="excluded", reason="licence_not_permissive")
    else:
        row["state"] = "eligible"
        row["reason"] = ""
    return row


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(REPO_DIR, exist_ok=True)
    with open(FRAME, newline="", encoding="utf-8") as f:
        repos = [r["repo"] for r in csv.DictReader(f)]
    if not repos:
        print("pilot: empty frame")
        return 1

    ordered = sorted(repos, key=lambda r: hashlib.sha256(f"{SEED}:{r}".encode()).hexdigest())
    print(f"pilot: frame={len(repos)} seed={SEED} first={ordered[0]}")

    rows: list[dict] = []
    eligible = 0
    for slug in ordered[:MAX_SCREEN]:
        row = screen(slug)
        rows.append(row)
        if row["state"] == "eligible":
            eligible += 1
        else:
            # Free disk: excluded clones are not needed and the screen.csv row is
            # the evidence. Eligible clones are kept for the build attempt.
            dest = os.path.join(REPO_DIR, slug.replace("/", "__", 1))
            shutil.rmtree(dest, ignore_errors=True)
        print(f"  {row['state']:9s} {slug:52s} {row['reason']:24s} "
              f"feat={row['n_features']:3d} scen={row['n_scenarios']:4d} lic={row['licence'][:14]}")
        if eligible >= TARGET_ELIGIBLE:
            print(f"pilot: reached {eligible} eligible, stopping screen")
            break

    out = os.path.join(OUT_DIR, "screen.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    states = Counter(r["state"] for r in rows)
    reasons = Counter(r["reason"] for r in rows if r["reason"])
    tested = len(rows)
    n_elig = states.get("eligible", 0)

    # Wilson score 95% interval for the eligible proportion: the point of the
    # pilot is an interval for achievable yield, not a bare percentage.
    def wilson(k: int, n: int, z: float = 1.959963985) -> tuple[float, float]:
        if n == 0:
            return (0.0, 1.0)
        p = k / n
        denom = 1 + z * z / n
        centre = (p + z * z / (2 * n)) / denom
        half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / denom
        return (max(0.0, centre - half), min(1.0, centre + half))

    lo, hi = wilson(n_elig, tested)

    with open(os.path.join(OUT_DIR, "PILOT.md"), "w", encoding="utf-8") as f:
        f.write("# P1.5 pilot — screening yield\n\n")
        f.write(f"- Frame size `N_frame`: **{len(repos)}**\n")
        f.write(f"- Sampling seed: **{SEED}** (hash-ordered permutation of frame)\n")
        f.write(f"- Repositories attempted: **{tested}**\n")
        f.write(f"- Eligible after static screen: **{n_elig}** "
                f"({100.0 * n_elig / max(tested, 1):.1f} %; 95 % Wilson CI "
                f"{100.0 * lo:.1f}–{100.0 * hi:.1f} %)\n")
        f.write(f"- Extrapolated eligible pool in frame at this yield: "
                f"**{lo * len(repos):.0f}–{hi * len(repos):.0f}** repositories\n\n")
        if n_elig < 30:
            f.write(f"> **The frame as currently defined cannot reach the design target of n = 30.**\n"
                    f"> At the upper 95 % bound this frame yields at most ~{hi * len(repos):.0f} "
                    f"statically eligible repositories before any build attrition,\n"
                    f"> and build attrition can only remove repositories. **This is a gate decision.**\n\n")
        f.write("## Funnel states\n\n| State | n |\n|---|---|\n")
        for s, n in states.most_common():
            f.write(f"| {s} | {n} |\n")
        f.write("\n## Exclusion reasons (categorised)\n\n| Reason | n | share |\n|---|---|---|\n")
        for r, n in reasons.most_common():
            f.write(f"| {r} | {n} | {100.0 * n / max(tested, 1):.1f} % |\n")
        f.write("\n## Scenario-count distribution (all attempted)\n\n"
                "| scenarios | n |\n|---|---|\n")
        buckets = Counter()
        for r in rows:
            s = int(r["n_scenarios"])
            buckets[">=20" if s >= 20 else "10-19" if s >= 10 else "5-9" if s >= 5 else "<5"] += 1
        for b in (">=20", "10-19", "5-9", "<5"):
            f.write(f"| {b} | {buckets.get(b, 0)} |\n")
        f.write("\n## Licence presence (all attempted)\n\n| licence | n |\n|---|---|\n")
        for lic, n in Counter(r["licence"] for r in rows).most_common():
            f.write(f"| `{lic}` | {n} |\n")
        f.write("\n## Eligible repositories\n\n")
        elig = [r for r in rows if r["state"] == "eligible"]
        if elig:
            for r in elig:
                f.write(f"- `{r['repo']}` — {r['n_features']} features, {r['n_scenarios']} scenarios, "
                        f"licence `{r['licence']}`, build `{r['build_files']}`, "
                        f"last commit {r['last_commit']}\n")
        else:
            f.write("_None passed the static screen._\n")
        f.write("\n_Per-repo detail: `data/pilot/screen.csv`._\n")

    print(f"\npilot: {tested} attempted -> {n_elig} eligible "
          f"({100.0 * n_elig / max(tested,1):.1f} %, 95% CI {100.0*lo:.1f}-{100.0*hi:.1f})")
    print(f"pilot: reasons {dict(reasons)}")
    print(f"pilot: wrote {out} and data/pilot/PILOT.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
