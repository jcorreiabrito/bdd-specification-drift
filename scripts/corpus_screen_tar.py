#!/usr/bin/env python
"""P2 corpus screener v3 — stream screening from GitHub tarballs, no clones.

Why v3 exists: v2 cloned every candidate, and on this host (Windows + OneDrive)
recursive deletion silently failed, so excluded clones accumulated until the disk
was at risk. 428 stale clones had to be removed by hand.

v3 streams `https://codeload.github.com/<owner>/<repo>/tar.gz/HEAD` into memory and
inspects the archive **without extracting**. Only repositories that pass the static
screen are written to disk, for the later build/mutation stage. Consequences:
  * no accumulation of junk clones, so no disk pressure;
  * roughly one HTTP request per candidate instead of a full git clone;
  * the same eligibility rules as v2 (docs/method.md, frame v2 as approved at the
    P1.5 gate: licence + application shape + BDD runner in a manifest).

Eligibility (identical to v2):
  E1 >=1 .feature   E2 >=20 scenarios   E3 >=1 step-definition file
  E4 >=1 build descriptor  E5 permissive licence  E6 language in scope
  E7 >=10 non-test source files (application shape)  E8 BDD runner in a manifest

Outputs are appended per repository, so an interrupted run loses nothing:
    data/corpus/candidates.csv
    data/corpus/SCREENING.json   (rewritten at the end of each run)

Usage:
    python scripts/corpus_screen_tar.py --limit 300 --offset 0
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import tarfile
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone

SEED = 20261125
FRAME = os.path.join("data", "frame", "frame_repos.csv")
OUT_DIR = os.path.join("data", "corpus")
OUT = os.path.join(OUT_DIR, "candidates.csv")
REPO_DIR = os.path.join("data", "repos")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) bdd-spec-drift-research/1.0"
MAX_BYTES = 80 * 1024 * 1024
TIMEOUT = 150

MIN_SCENARIOS = 20
MIN_APP_SOURCES = 10
PERMISSIVE = ("mit", "apache", "bsd", "isc", "mpl", "lgpl", "gpl", "epl",
              "unlicense", "cc0", "cc-by", "artistic", "zlib")
BUILD_FILES = {"pom.xml", "build.gradle", "build.gradle.kts", "package.json",
               "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt",
               "build.sbt", "build.xml", "gradlew", "mvnw"}
BUILD_EXTS = (".csproj", ".fsproj", ".vbproj", ".sln")
SCENARIO_RX = re.compile(
    r"^\s*(Scenario|Scenario Outline|Scenario Template|Cenário|Cenário Esquema|Ejemplo)\s*:", re.M)
STEP_RX = [re.compile(r"@(?:Given|When|Then|And|But)\s*\("),
           re.compile(r"\[\s*(?:Given|When|Then|And|But)\s*\("),
           re.compile(r"^\s*(?:Given|When|Then|And|But)\s*[({\"']", re.M)]
BDD_DEP_RX = re.compile(r"(cucumber|behave|pytest[-_]bdd|playwright[-_]bdd|serenity|karate|"
                        r"specflow|reqnroll|gherkin)", re.I)
TEST_PATH_RX = re.compile(
    r"(^|/)(test|tests|spec|specs|__tests__|e2e|acceptance|integration[-_]?tests?|features?)(/|$)", re.I)
TEST_FILE_RX = re.compile(
    r"(Test|Tests|IT|Spec)\.(java|kt|groovy)$|_test\.py$|^test_.*\.py$|\.(test|spec)\.(js|jsx|ts|tsx)$", re.I)
LANG_BY_EXT = {".java": "java", ".kt": "java", ".groovy": "java",
               ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript",
               ".cjs": "javascript", ".ts": "typescript", ".tsx": "typescript",
               ".py": "python"}
SKIP_DIR = re.compile(r"(^|/)(\.git|node_modules|target|build|vendor|dist|\.gradle|"
                      r"__pycache__|\.venv|venv)(/|$)")

FIELDS = ["repo", "state", "reason", "language", "licence", "n_features", "n_scenarios",
          "n_step_files", "n_app_sources", "n_test_sources", "build_files", "bdd_runner",
          "n_files", "archive_bytes", "screened_utc"]


def fetch_tar(slug: str) -> tuple[int | None, bytes]:
    url = f"https://codeload.github.com/{slug}/tar.gz/HEAD"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                data = r.read(MAX_BYTES + 1)
                if len(data) > MAX_BYTES:
                    return 413, b""
                return r.status, data
        except urllib.error.HTTPError as e:
            if e.code in (404, 451):
                return e.code, b""
            time.sleep(1.5 * (attempt + 1))
        except Exception:  # noqa: BLE001 - 10054 resets are routine here
            time.sleep(1.5 * (attempt + 1))
    return None, b""


def scan_archive(slug: str, blob: bytes) -> tuple[dict, tarfile.TarFile | None]:
    row = {f: "" for f in FIELDS}
    row.update(repo=slug, n_features=0, n_scenarios=0, n_step_files=0,
               n_app_sources=0, n_test_sources=0, n_files=0,
               archive_bytes=len(blob),
               screened_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"))
    try:
        tf = tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz")
    except Exception:
        row.update(state="excluded", reason="archive_unreadable")
        return row, None

    features = scenarios = step_files = app_src = test_src = n_files = 0
    builds: list[str] = []
    licences: list[str] = []
    manifests: list[bytes] = []
    lang_votes: Counter = Counter()

    for m in tf.getmembers():
        if not m.isfile():
            continue
        name = m.name
        parts = name.split("/", 1)
        rel = parts[1] if len(parts) == 2 else name
        if SKIP_DIR.search(rel):
            continue
        n_files += 1
        low = rel.rsplit("/", 1)[-1].lower()
        if n_files > 60000:
            break
        if low in BUILD_FILES or low.endswith(BUILD_EXTS):
            builds.append(rel)
        if low in ("license", "license.md", "license.txt", "licence", "copying"):
            try:
                licences.append(tf.extractfile(m).read(8000).decode("utf-8", "replace").lower())
            except Exception:
                pass
        if low in ("package.json", "pyproject.toml", "pom.xml", "setup.py", "build.gradle", "build.gradle.kts"):
            try:
                manifests.append(tf.extractfile(m).read(200000))
            except Exception:
                pass
        if low.endswith(".feature"):
            features += 1
            try:
                scenarios += len(SCENARIO_RX.findall(
                    tf.extractfile(m).read(400000).decode("utf-8", "replace")))
            except Exception:
                pass
            continue
        ext = os.path.splitext(low)[1]
        if ext not in LANG_BY_EXT:
            continue
        try:
            head = tf.extractfile(m).read(20000).decode("utf-8", "replace")
        except Exception:
            head = ""
        if any(p.search(head) for p in STEP_RX):
            step_files += 1
        if TEST_FILE_RX.search(low) or TEST_PATH_RX.search("/" + rel):
            test_src += 1
        else:
            app_src += 1
            lang_votes[LANG_BY_EXT[ext]] += 1

    licence = "none_found"
    for txt in licences:
        for k in PERMISSIVE:
            if k in txt:
                licence = k
                break
        if licence != "none_found":
            break
    bdd_runner = ""
    joined = b"\n".join(manifests).decode("utf-8", "replace")
    hit = BDD_DEP_RX.search(joined)
    if hit:
        bdd_runner = hit.group(1).lower()

    row.update(n_features=features, n_scenarios=scenarios, n_step_files=step_files,
               n_app_sources=app_src, n_test_sources=test_src, n_files=n_files,
               build_files=";".join(sorted(builds)[:4]), bdd_runner=bdd_runner,
               licence=licence,
               language=(lang_votes.most_common(1)[0][0] if lang_votes else "unknown"))

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
    elif not any(k in licence for k in PERMISSIVE):
        row.update(state="excluded", reason="licence_not_permissive")
    elif not bdd_runner:
        row.update(state="excluded", reason="no_bdd_runner_dependency")
    elif app_src < MIN_APP_SOURCES:
        row.update(state="excluded", reason="no_application_shape")
    else:
        row.update(state="eligible", reason="")
        # Materialise ONLY eligible repositories, for the build/mutation stage.
        # Strip the archive's single top-level directory so the project sits at the
        # repository root: path-based domain detection and build discovery both
        # assume that layout.
        dest = os.path.join(REPO_DIR, slug.replace("/", "__", 1))
        if not os.path.isdir(dest):
            os.makedirs(dest, exist_ok=True)
            for m in tf.getmembers():
                if not (m.isfile() or m.isdir()):
                    continue
                parts = m.name.split("/", 1)
                if len(parts) != 2 or not parts[1]:
                    continue
                rel = parts[1]
                if rel.startswith("/") or ".." in rel.split("/"):
                    continue
                target = os.path.join(dest, *rel.split("/"))
                if m.isdir():
                    os.makedirs(target, exist_ok=True)
                    continue
                os.makedirs(os.path.dirname(target), exist_ok=True)
                try:
                    src = tf.extractfile(m)
                    if src is None:
                        continue
                    with open(target, "wb") as out:
                        out.write(src.read())
                    os.chmod(target, 0o644)
                except Exception:
                    continue
    return row, tf


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--offset", type=int, default=0)
    a = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(REPO_DIR, exist_ok=True)

    with open(FRAME, newline="", encoding="utf-8") as f:
        repos = [r["repo"] for r in csv.DictReader(f)]
    ordered = sorted(repos, key=lambda r: hashlib.sha256(f"{SEED}:{r}".encode()).hexdigest())

    done: set[str] = set()
    if os.path.exists(OUT):
        with open(OUT, newline="", encoding="utf-8") as f:
            done = {r["repo"] for r in csv.DictReader(f)}

    batch = [r for r in ordered if r not in done][a.offset: a.offset + a.limit]
    new_file = not os.path.exists(OUT)
    fout = open(OUT, "a", newline="", encoding="utf-8")
    w = csv.DictWriter(fout, fieldnames=FIELDS)
    if new_file:
        w.writeheader()

    try:
        for i, slug in enumerate(batch, 1):
            code, blob = fetch_tar(slug)
            if code != 200 or not blob:
                row = {f: "" for f in FIELDS}
                row.update(repo=slug, state="excluded", reason=f"fetch_failed_{code}",
                           screened_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"))
            else:
                row, _ = scan_archive(slug, blob)
            w.writerow(row)
            fout.flush()
            if i % 10 == 0 or row["state"] == "eligible":
                print(f"  [{i}/{len(batch)}] {row['state']:9s} {row['reason']:26s} "
                      f"{row.get('language',''):11s} {slug}", flush=True)
    finally:
        fout.close()

    with open(OUT, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    states = Counter(r["state"] for r in rows)
    reasons = Counter(r["reason"] for r in rows if r["reason"])
    elig = [r for r in rows if r["state"] == "eligible"]
    langs = Counter(r["language"] for r in elig)
    summary = {"total_screened": len(rows), "eligible": len(elig),
               "yield_pct": round(100.0 * len(elig) / max(len(rows), 1), 2),
               "reasons": dict(reasons.most_common()),
               "eligible_by_language": dict(langs),
               "seed": SEED, "updated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    with open(os.path.join(OUT_DIR, "SCREENING.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
