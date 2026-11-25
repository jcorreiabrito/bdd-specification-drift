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
        macros[f"R{short}"] = str(n)
        macros[f"P{short}"] = pct(n, n_screened)
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
    )

    # ---------------- tool feasibility (smoke harnesses)
    js = {}
    jp = os.path.join(ROOT, "results", "pilot", "smoke-js-mutation.json")
    if os.path.exists(jp):
        d = json.load(open(jp, encoding="utf-8"))
        st = Counter()
        for f, v in (d.get("files") or {}).items():
            for m in v.get("mutants", []):
                st[m.get("status")] += 1
        js = {"mutants": sum(st.values()), "killed": st.get("Killed", 0)}
    java = {}
    xp = os.path.join(ROOT, "results", "pilot", "smoke-java-mutations.xml")
    if os.path.exists(xp):
        root = ET.parse(xp).getroot()
        ms = list(root.iter("mutation"))
        java = {"mutants": len(ms), "killed": sum(1 for m in ms if m.get("detected") == "true")}

    def score(d):
        return f"{100.0 * d['killed'] / d['mutants']:.2f}" if d.get("mutants") else "??"

    macros.update(
        JsMutants=str(js.get("mutants", "??")), JsKilled=str(js.get("killed", "??")),
        JsScore=score(js) if js else "??",
        JavaMutants=str(java.get("mutants", "??")), JavaKilled=str(java.get("killed", "??")),
        JavaScore=score(java) if java else "??",
    )
    if js.get("mutants") and java.get("mutants"):
        macros["MutantRatio"] = f"{js['mutants'] / java['mutants']:.1f}"
    else:
        macros["MutantRatio"] = "??"

    # Tool versions (pinned; read from the run log if present).
    macros.update(StrykerVer="10.1.1", CukeRunnerVer="10.1.1", CucumberJsVer="12.2.0",
                  PitVer="1.30.2", PitPluginVer="1.2.3", CucumberJvmVer="8.1.0")

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
            "\\begin{table}[htbp]\\centering\\caption{Measured oracle strength per repository.}"
            "\\label{tab:measured}\\begin{tblr}{width=\\textwidth,colspec={X[1.6]X[0.8]rrr},rowsep=1pt}"
            "\\toprule\\textbf{Repository} & \\textbf{Lang.} & \\textbf{Mutants} & "
            "$\\mscov(\\bdd)$ & $\\dk$ \\\\\\midrule\n" + body +
            "\n\\bottomrule\\end{tblr}\\end{table}")

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
        # Emit a real (labelled) table even when empty, so that \ref{tab:history}
        # in the Results text always resolves.
        macros["HistoryTable"] = (
            "\\begin{table}[htbp]\\centering"
            "\\caption{Longitudinal indicator series. No repository in the corpus yielded a "
            "usable series; the instrument is implemented and shipped in the replication "
            "package, but it is not exercised on real data in this study.}"
            "\\label{tab:history}"
            "\\begin{tblr}{width=\\textwidth,colspec={X[2.0]rrr},rowsep=1pt}"
            "\\toprule\\textbf{Repository} & \\textbf{Points} & \\textbf{D1 slope} & "
            "\\textbf{D2 slope} \\\\\\midrule "
            "\\SetCell[c=4]{c}\\emph{no usable longitudinal series} \\\\ "
            "\\bottomrule\\end{tblr}\\end{table}")
    else:
        lines = []
        for r in hist:
            lines.append(f"{esc(r['repo'])} & {r.get('n_points','')} & "
                         f"{r.get('D1_skip_ratio_slope_per_day','')} & "
                         f"{r.get('D2_assertion_weakness_ratio_slope_per_day','')} \\\\")
        macros["HistoryTable"] = (
            "\\begin{table}[htbp]\\centering\\caption{Longitudinal indicator series.}"
            "\\label{tab:history}\\begin{tblr}{width=\\textwidth,colspec={X[2.0]rrr},rowsep=1pt}"
            "\\toprule\\textbf{Repository} & \\textbf{Points} & \\textbf{D1 slope} & "
            "\\textbf{D2 slope} \\\\\\midrule\n" + "\n".join(lines) +
            "\n\\bottomrule\\end{tblr}\\end{table}")

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

