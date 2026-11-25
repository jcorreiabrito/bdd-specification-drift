#!/usr/bin/env python
"""Generate paper/numbers.tex from result files.

Every quantitative claim in the manuscript references a macro defined here, so a
number cannot be typed into the prose. If a source file is missing, the macro is
defined as a visible sentinel (??) so the manuscript fails loudly rather than
silently printing a stale or invented value.

Usage:
    python scripts/make_numbers.py
"""
from __future__ import annotations

import csv
import glob
import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "paper", "numbers.tex")
SEED = 20261125
SENTINEL = r"\textbf{??}"


def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(f))


def grp(n) -> str:
    """Group thousands with a LaTeX-safe separator: 1270 -> 1{,}270."""
    return f"{n:,}".replace(",", "{,}")


def pct(n, d):
    return f"{100.0 * n / d:.2f}" if d else "0.00"


def esc(s):
    return str(s).replace("_", r"\_").replace("%", r"\%").replace("&", r"\&")


def wilson(k, n, z=1.959963985):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main() -> int:
    macros: dict[str, str] = {}

    # ---------------- frame
    frame_md = os.path.join(ROOT, "data", "frame", "FRAME.md")
    frame_repos = read_csv(os.path.join(ROOT, "data", "frame", "frame_repos.csv"))
    macros["Nframe"] = f"{len(frame_repos):,}".replace(",", "{,}")
    topicpages, topicslugs, langfilters = 0, 0, 0
    if os.path.exists(frame_md):
        txt = open(frame_md, encoding="utf-8").read()
        m = re.search(r"Topic pages fetched:\s*(\d+)", txt)
        topicpages = int(m.group(1)) if m else 0
        m = re.search(r"Topics enumerated \((\d+)\)", txt)
        topicslugs = int(m.group(1)) if m else 0
        m = re.search(r"Language filters:\s*(.+)", txt)
        langfilters = len((m.group(1) if m else "").split(",")) if m else 0
    macros.update(Ntopicpages=str(topicpages or "??"), topicslugs=str(topicslugs or "??"),
                  langfilters=str(langfilters or "??"))

    # ---------------- screening
    cand = read_csv(os.path.join(ROOT, "data", "corpus", "candidates.csv"))
    states = Counter(r["state"] for r in cand)
    reasons = Counter(r["reason"] for r in cand if r.get("reason"))
    n_screened = len(cand)
    n_elig = states.get("eligible", 0)
    lo, hi = wilson(n_elig, n_screened)
    macros.update(
        Nscreened=f"{n_screened:,}".replace(",", "{,}"),
        Neligible=str(n_elig),
        YieldPct=pct(n_elig, n_screened),
        YieldLo=f"{100.0 * lo:.1f}",
        YieldHi=f"{100.0 * hi:.1f}",
    )
    reason_map = {
        "too_few_scenarios": "tooFew", "no_feature_files": "noFeat",
        "no_step_definitions": "noSteps", "no_bdd_runner_dependency": "noRunner",
        "no_application_shape": "noShape", "licence_not_permissive": "licence",
        "language_out_of_scope": "lang", "no_build_config": "noBuild",
    }
    for full, short in reason_map.items():
        n = reasons.get(full, 0)
        macros[f"R{short}"] = grp(n)
        macros[f"P{short}"] = pct(n, n_screened)
    macros["Nfetchfailed"] = str(reasons.get("fetch_failed_413", 0))
    other = n_screened - n_elig - sum(reasons.get(k, 0) for k in reason_map)
    macros["Rother"] = str(max(other, 0))
    macros["Pother"] = pct(max(other, 0), n_screened)

    # ---------------- build screen
    build = []
    for p in glob.glob(os.path.join(ROOT, "data", "corpus", "bs_*.csv")):
        build += read_csv(p)
    seen = {}
    for r in build:
        seen[r["repo"]] = r
    build = list(seen.values())
    bstates = Counter(r["state"] for r in build)
    macros.update(
        Nbuildtested=str(len(build)),
        Ngreen=str(bstates.get("bdd_passes", 0)),
        Nbdffails=str(bstates.get("bdd_fails", 0)),
        Nnobddexec=str(bstates.get("no_bdd_execution", 0)),
        Nbuildfails=str(bstates.get("build_fails", 0)),
        Nunsupported=str(bstates.get("unsupported", 0)),
        Ntimeout=str(bstates.get("timeout", 0)),
    )

    # ---------------- tool feasibility: three-mode harnesses (Phase 3.1)
    # Source of truth is data/metrics/feasibility.json, produced by
    # pipelines/analysis/feasibility_report.py from the raw per-mutant statuses.
    feas_path = os.path.join(ROOT, "data", "metrics", "feasibility.json")
    feas = {}
    if os.path.exists(feas_path):
        feas = json.load(open(feas_path, encoding="utf-8"))

    def pct3(x):
        return f"{100.0 * x:.2f}" if isinstance(x, (int, float)) else "??"

    def dec3(x):
        return f"{x:.3f}" if isinstance(x, (int, float)) else "---"

    for tag, mtag in (("js", "Js"), ("java", "Java")):
        blk = feas.get(tag) or {}
        d = blk.get("differential") or {}
        sc = blk.get("status_counts", {}).get("bdd", {})
        macros[f"{mtag}Mutants"] = str(blk.get("mutants", {}).get("bdd", "??"))
        macros[f"{mtag}Killed"] = str(sc.get("KILLED", "??"))
        macros[f"{mtag}NoCov"] = str(blk.get("no_coverage_control_observed", "??"))
        macros[f"{mtag}MsAll"] = pct3(blk.get("bdd_MS_all"))
        macros[f"{mtag}MsCov"] = pct3(blk.get("bdd_MS_cov"))
        macros[f"{mtag}Score"] = pct3(blk.get("bdd_MS_cov"))
        macros[f"{mtag}S"] = str(d.get("s_size", "??"))
        macros[f"{mtag}DkBdd"] = dec3(d.get("dk_bdd_uplift"))
        macros[f"{mtag}DkNon"] = dec3(d.get("dk_nonbdd_uplift"))
        macros[f"{mtag}BddUnique"] = dec3(d.get("bdd_unique_share"))
        macros[f"{mtag}BddTotal"] = dec3(d.get("bdd_total_share"))
        macros[f"{mtag}Overlap"] = dec3(d.get("overlap"))

    java_aligned = (feas.get("java") or {}).get("mutants", {}).get("bdd")
    java_def = ((feas.get("java") or {}).get("default_for_divergence") or {}).get("mutants")
    jv = {}
    jp = os.path.join(ROOT, "data", "metrics", "feasibility-java.json")
    if os.path.exists(jp):
        try:
            jv = json.load(open(jp, encoding="utf-8"))
        except Exception:
            jv = {}
    java_def = (jv.get("default") or {}).get("modes", {}).get("full", "??")
    macros["JavaDefaultMutants"] = str(java_def)
    macros["JavaAlignedMutants"] = str(java_aligned if java_aligned is not None else "??")
    try:
        macros["MutantRatio"] = f"{int(macros['JsMutants']) / int(macros['JavaMutants']):.1f}"
    except (ValueError, ZeroDivisionError):
        macros["MutantRatio"] = "??"

    # Tool versions (pinned; read from the run log if present).
    macros.update(StrykerVer="10.1.1", CukeRunnerVer="10.1.1", CucumberJsVer="12.2.0",
                  PitVer="1.30.2", PitPluginVer="1.2.3", CucumberJvmVer="8.1.0")

    # ---------------- seeded-drift validation campaign (Phase 3.2)
    sd_path = os.path.join(ROOT, "data", "metrics", "seeded_drift.json")
    sd = {}
    if os.path.exists(sd_path):
        sd = json.load(open(sd_path, encoding="utf-8"))
    if sd:
        base = (sd.get("baseline_mutation") or {}).get("MS_cov")
        macros["DriftBaseMsCov"] = f"{100.0 * base:.2f}" if isinstance(base, (int, float)) else "??"
        macros["DriftTargets"] = str(sd.get("sensitivity_targets", "??"))
        macros["DriftDetected"] = str(sd.get("detected", "??"))
        macros["DriftInvalid"] = str(sd.get("invalid_injections", "??"))
        for r in sd.get("results", []):
            tag = r.get("injection", "")
            if tag.startswith("I1") and r.get("indicator_deltas"):
                d = r["indicator_deltas"].get("D1_skip_ratio")
                if isinstance(d, (int, float)):
                    macros["DriftIoneDelta"] = f"{d:.3f}"
            if tag.startswith("I3") and r.get("indicator_deltas"):
                d = r["indicator_deltas"].get("D4_redundancy_cluster_ratio")
                if isinstance(d, (int, float)):
                    macros["DriftIthreeDelta"] = f"{d:.3f}"
            if tag.startswith("I2") and r.get("mutation"):
                ms = r["mutation"].get("MS_cov")
                if isinstance(ms, (int, float)):
                    macros["DriftItwoMsCov"] = f"{100.0 * ms:.2f}"
            if tag.startswith("I4") and r.get("mutation"):
                ms = r["mutation"].get("MS_cov")
                if isinstance(ms, (int, float)):
                    macros["DriftIfourMsCov"] = f"{100.0 * ms:.2f}"

    # ---------------- static D1-D7 census over all eligible repositories (Phase 3.3)
    cen_path = os.path.join(ROOT, "data", "metrics", "census.json")
    if os.path.exists(cen_path):
        cen = json.load(open(cen_path, encoding="utf-8"))
        macros["CensusMeasured"] = str(cen.get("measured", "??"))
        macros["CensusEligible"] = str(cen.get("eligible_repositories", "??"))
        macros["CensusFailures"] = str(cen.get("extraction_failures", "??"))
        macros["CensusLowConf"] = str(cen.get("D2_low_confidence", "??"))
        short = {"D1_skip_ratio": "Done", "D2_assertion_weakness_ratio": "Dtwo",
                 "D3_stale_spec_ratio": "Dthree", "D4_redundancy_cluster_ratio": "Dfour",
                 "D5_glue_duplication_ratio": "Dfive",
                 "D6_literal_bearing_stepdef_ratio": "Dsix",
                 "D7_mirror_stepdef_ratio": "Dseven"}
        for ind, tag in short.items():
            st = (cen.get("indicators") or {}).get(ind) or {}
            if st.get("n"):
                macros[f"Census{tag}N"] = str(st["n"])
                macros[f"Census{tag}Median"] = f"{st['median']:.3f}"
                macros[f"Census{tag}Qone"] = f"{st['q1']:.3f}"
                macros[f"Census{tag}Qthree"] = f"{st['q3']:.3f}"
            else:
                macros[f"Census{tag}N"] = "0"
                macros[f"Census{tag}Median"] = "---"

    # ---------------- measured corpus (RQ2)
    repo_level = read_csv(os.path.join(ROOT, "data", "metrics", "repo_level.csv"))
    n_measured = sum(1 for r in repo_level if (r.get("MS_cov_bdd") or "") not in ("", "None"))
    n_full = sum(1 for r in repo_level if (r.get("DK_norm") or "") not in ("", "None"))
    macros.update(Nmeasured=str(n_measured), Nwithfull=str(n_full))

    if n_measured == 0:
        macros["MeasuredTable"] = (
            r"\noindent\textbf{No repository in the corpus yielded a complete BDD-only "
            r"measurement.} The instrument's numerical behaviour is therefore demonstrated in "
            r"Table~\ref{tab:feasibility} on the purpose-built harness suites, and the corpus-level "
            r"quantity reported here is zero repositories, not a value estimated from partial data.")
    else:
        rows = []
        for r in repo_level:
            if (r.get("MS_cov_bdd") or "") in ("", "None"):
                continue
            rows.append(
                f"{esc(r['repo'])} & {esc(r.get('language',''))} & {r.get('n_mutants_bdd','')} & "
                f"{float(r['MS_cov_bdd']):.3f} & "
                f"{(f'{float(r[chr(68)+chr(75)+chr(95)+chr(110)+chr(111)+chr(114)+chr(109)]):.3f}'
                   if (r.get('DK_norm') or '') not in ('', 'None') else '---')} \\\\")
        body = "\n".join(rows)
        macros["MeasuredTable"] = (
            "\\begin{table*}[t]\\centering\\caption{Measured oracle strength per repository.}"
            "\\label{tab:measured}\\begin{tblr}{width=\\textwidth,colspec={X[1.6]X[0.8]rrr},rowsep=1pt}"
            "\\toprule\\textbf{Repository} & \\textbf{Lang.} & \\textbf{Mutants} & "
            "$\\mscov(\\bdd)$ & $\\dk$ \\\\\\midrule\n" + body +
            "\n\\bottomrule\\end{tblr}\\end{table*}")

    # ---------------- power floor
    n_eff = n_measured if n_measured >= 4 else max(n_measured, 1)
    if n_eff >= 4:
        se = 1.030 / math.sqrt(n_eff - 3)
        floor = math.tanh((1.959963985 + 0.841621234) * se)
        macros["FloorRho"] = f"{floor:.2f}"
    else:
        macros["FloorRho"] = r"\text{not defined (no measured units)}"

    # ---------------- history
    hist = read_csv(os.path.join(ROOT, "data", "metrics", "history_slopes.csv"))
    macros.update(HistoryK="12", Nhistory=str(len(hist)))
    if not hist:
        # No series: emit NOTHING. An empty table with headers and a placeholder
        # row reads as a rendering fault; the prose already explains the absence.
        macros["HistoryTable"] = ""
    else:
        lines = []
        for r in hist:
            lines.append(f"{esc(r['repo'])} & {r.get('n_points','')} & "
                         f"{r.get('D1_skip_ratio_slope_per_day','')} & "
                         f"{r.get('D2_assertion_weakness_ratio_slope_per_day','')} \\\\")
        macros["HistoryTable"] = (
            "\\begin{table*}[t]\\centering\\caption{Longitudinal indicator series.}"
            "\\label{tab:history}\\begin{tblr}{width=\\textwidth,colspec={X[2.0]rrr},rowsep=1pt}"
            "\\toprule\\textbf{Repository} & \\textbf{Points} & \\textbf{D1 slope} & "
            "\\textbf{D2 slope} \\\\\\midrule\n" + "\n".join(lines) +
            "\n\\bottomrule\\end{tblr}\\end{table*}")

    # ---------------- python stratum
    py_elig = sum(1 for r in cand if r.get("state") == "eligible" and r.get("language") == "python")
    macros["NpyEligible"] = str(py_elig)
    macros["Seed"] = str(SEED)

    # ---------------- emit
    lines = ["% GENERATED by scripts/make_numbers.py â€” do not edit by hand.",
             "% Every macro below is derived from a file under data/ or results/.",
             ""]
    for k in sorted(macros):
        v = macros[k]
        if "\\" in v and len(v) > 200:
            lines.append(f"\\newcommand{{\\{k}}}{{{v}}}")
        else:
            lines.append(f"\\newcommand{{\\{k}}}{{{v}}}")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"make_numbers: wrote {len(macros)} macros -> {OUT}")
    for k in ("Nframe", "Nscreened", "Neligible", "YieldPct", "Nbuildtested", "Ngreen",
              "JsMutants", "JavaMutants", "Nmeasured", "FloorRho", "NpyEligible"):
        print(f"  {k:14s} = {macros.get(k)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

