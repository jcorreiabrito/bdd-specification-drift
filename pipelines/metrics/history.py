#!/usr/bin/env python
"""Longitudinal drift mining (RQ3): indicators across K deterministically sampled commits.

Method (docs/method.md section 13.1): for each repository, walk the history that
touches `.feature` files, step definitions or the domain layer, sample K = 12
commits spanning the lifetime at even index positions, and recompute the static
indicators at each.

Implementation choice: at each sampled commit we `git archive` the tree into a
temporary directory and run the SAME indicator code used at HEAD
(`pipelines/metrics/static_metrics.py`). Reusing one implementation is the point —
computing history with a second, subtly different parser would make the trend an
artefact of the two parsers disagreeing.

Known limitation, disclosed in the paper: the archived tree has no `.git`, so
D3 (stale specs via `git blame`) is NOT computed per commit; it is computed only at
HEAD from the real clone. D1, D2, D4, D5, D6, D7 are computed per commit.

Trend statistic: Theil-Sen slope of the indicator against commit time (days since
the repository's first commit), which is distribution-free and robust for short
series. Reported with the proportion of positive slopes and an exact binomial CI.

Outputs:
    data/metrics/history/<owner>__<repo>.csv      per-commit indicator series
    data/metrics/history_slopes.csv               one row per repo per indicator

Usage:
    python pipelines/metrics/history.py --repo owner/name
"""
from __future__ import annotations

import argparse
import csv
import io
import math
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from itertools import combinations

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "pipelines", "metrics"))
import static_metrics as sm  # noqa: E402

REPO_DIR = os.path.join(ROOT, "data", "repos")
OUT_HIST = os.path.join(ROOT, "data", "metrics", "history")
OUT_SLOPES = os.path.join(ROOT, "data", "metrics", "history_slopes.csv")
K = 12
INDICATORS = ["D1_skip_ratio", "D2_assertion_weakness_ratio", "D4_redundancy_cluster_ratio",
              "D5_glue_duplication_ratio", "D6_literal_bearing_stepdef_ratio",
              "D7_mirror_stepdef_ratio", "n_scenarios", "n_step_defs"]


def git(repo: str, *args, timeout=300):
    try:
        p = subprocess.run(["git", "-C", repo, *args], capture_output=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return p.returncode, p.stdout
    except Exception:
        return 1, ""


def theil_sen(xs: list[float], ys: list[float]) -> float | None:
    slopes = []
    for (i, j) in combinations(range(len(xs)), 2):
        dx = xs[j] - xs[i]
        if dx != 0:
            slopes.append((ys[j] - ys[i]) / dx)
    if not slopes:
        return None
    slopes.sort()
    n = len(slopes)
    return slopes[n // 2] if n % 2 else (slopes[n // 2 - 1] + slopes[n // 2]) / 2


def commits_touching(repo: str) -> list[tuple[str, int]]:
    code, out = git(repo, "log", "--reverse", "--date=unix",
                    "--format=%H|%ct", "--",
                    "*.feature", ":(glob)**/*Step*.java", ":(glob)**/*Steps*.java",
                    ":(glob)**/steps/*.js", ":(glob)**/steps/*.ts",
                    ":(glob)**/steps/*.py", ":(glob)**/step_definitions/*", ":(glob)**/features/*")
    if code != 0:
        return []
    rows = []
    for line in out.strip().splitlines():
        if "|" in line:
            sha, ct = line.split("|", 1)
            try:
                rows.append((sha.strip(), int(ct.strip())))
            except ValueError:
                continue
    return rows


def archive_at(repo: str, sha: str, dest: str) -> bool:
    try:
        p = subprocess.run(["git", "-C", repo, "archive", "--format=tar", sha],
                           capture_output=True, timeout=300)
        if p.returncode != 0 or not p.stdout:
            return False
        with tarfile.open(fileobj=io.BytesIO(p.stdout), mode="r:") as tf:
            tf.extractall(dest)
        return True
    except Exception:
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--k", type=int, default=K)
    a = ap.parse_args()
    repo = a.repo
    d = os.path.join(REPO_DIR, repo.replace("/", "__", 1))
    if not os.path.isdir(os.path.join(d, ".git")):
        print(f"history: no .git for {repo}; skipping")
        return 1

    commits = commits_touching(d)
    if len(commits) < 2:
        print(f"history: {repo} has {len(commits)} relevant commits; skipping")
        return 1

    n = len(commits)
    k = min(a.k, n)
    idx = sorted({round(i * (n - 1) / (k - 1)) for i in range(k)}) if k > 1 else [0]
    t0 = commits[0][1]
    tmp_root = tempfile.mkdtemp(prefix="hist_")
    series = []
    try:
        for j in idx:
            sha, ct = commits[j]
            dest = os.path.join(tmp_root, f"c{j}_{sha[:8]}")
            os.makedirs(dest, exist_ok=True)
            if not archive_at(d, sha, dest):
                continue
            try:
                row, _ = sm.compute(repo, dest)
            except Exception as e:  # noqa: BLE001
                print(f"  compute failed at {sha[:8]}: {e}")
                continue
            rec = {"repo": repo, "sha": sha, "commit_utc": datetime.fromtimestamp(ct, tz=timezone.utc).isoformat(timespec="seconds"),
                   "days_since_first": round((ct - t0) / 86400.0, 2)}
            for ind in INDICATORS:
                rec[ind] = row.get(ind)
            series.append(rec)
            shutil.rmtree(dest, ignore_errors=True)
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    if len(series) < 3:
        print(f"history: {repo} yielded {len(series)} usable commits; skipping")
        return 1

    os.makedirs(OUT_HIST, exist_ok=True)
    hist_path = os.path.join(OUT_HIST, repo.replace("/", "__", 1) + ".csv")
    with open(hist_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(series[0].keys()))
        w.writeheader()
        w.writerows(series)

    xs = [r["days_since_first"] for r in series]
    slopes = {"repo": repo, "n_points": len(series)}
    for ind in INDICATORS:
        ys = []
        xk = []
        for r in series:
            v = r[ind]
            if v in (None, "", "None"):
                continue
            try:
                ys.append(float(v))
                xk.append(float(r["days_since_first"]))
            except (TypeError, ValueError):
                continue
        slopes[ind + "_slope_per_day"] = theil_sen(xk, ys) if len(ys) >= 3 else None
        slopes[ind + "_first"] = ys[0] if ys else None
        slopes[ind + "_last"] = ys[-1] if ys else None

    new = not os.path.exists(OUT_SLOPES)
    with open(OUT_SLOPES, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(slopes.keys()))
        if new:
            w.writeheader()
        w.writerow(slopes)
    print(f"history: {repo} -> {len(series)} points; "
          f"D1 slope={slopes.get('D1_skip_ratio_slope_per_day')}, "
          f"D2 slope={slopes.get('D2_assertion_weakness_ratio_slope_per_day')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
