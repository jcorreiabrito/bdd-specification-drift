# bdd-specification-drift

Replication package and manuscript for:

> **Do Public BDD Suites Still Work as Oracles? A Mutation-Based Instrument for Detecting
> Executable-Specification Drift in Cucumber-Style Suites**
> Submitted to *iSys — Revista Brasileira de Sistemas de Informação* (SBC/CESI).

The study builds a mutation-based instrument for measuring whether a Cucumber specification layer still
functions as an **oracle** (can it detect a change in the business rule it describes?), proves tool
feasibility in the Java and JavaScript/TypeScript ecosystems, and applies it to a pre-registered frame
of 2,552 public repositories.

**Headline result, stated honestly:** of 2,552 repositories screened, 94 were statically eligible
(3.68 %) and, of the 18 that were build/execution-tested, **none** produced a green, genuinely
executing Gherkin baseline. The paper is therefore a contribution of an *instrument* plus a
*quantified population/attrition finding* — not a measured correlation between drift indicators and
oracle strength. The manuscript says so explicitly, including in the abstract.

---

## What is in here

| Path | What it is |
|---|---|
| `paper/` | The manuscript. `main.tex` + `sections/*.tex` + generated `numbers.tex` and `refs.bib`. |
| `paper/out/main.pdf` | The built PDF (18 pages; iSys requires a minimum of 15). |
| `docs/method.md` | The pre-registered protocol: frame, eligibility, metrics, mutation protocol, statistics. |
| `docs/PROTOCOL.md` | The practical artefact: a five-step protocol a team can apply to its own suite. |
| `docs/GATE-1.5-REPORT.md` | The P1.5 human-review report (novelty, feasibility, pilot yield). |
| `docs/redteam.md` | Adversarial review of the study and the manuscript, and how each objection was answered. |
| `docs/DEVIATIONS.md` | Every departure from the plan, with reason and timestamp. |
| `lit/novelty.md` | The novelty claim, the prior work that narrows it, and the claims that are now forbidden. |
| `refs/verified.csv` | 78 references, each with a Crossref-resolved DOI. |
| `refs/RETRIEVALS.md` | Non-trivial retrievals, workarounds and disclosed access limitations. |
| `submission/` | Cover letter, venue rules with verbatim quotes, and the compliance checklist. |
| `results/RUNLOG.md` | Append-only evidence log: command, UTC timestamp, git SHA, host, seed, tool versions. |
| `data/frame/` | The sampling frame with snapshot timestamp and SHA-256 of the fetched pages. |
| `data/corpus/` | Screening and build/execution results, every repository in exactly one funnel state. |
| `pipelines/`, `scripts/` | Enumeration, screening, metrics, mutation and analysis code. |

## Requirements

Verified on: Windows 10.0.26300, Windows PowerShell 5.1, Python 3.12.4, Node v24.11.0, npm 11.6.1,
Oracle JDK 22.0.1, MiKTeX 25.12.

* Python 3.10+ (`pypdf` only for PDF text extraction; the analysis itself is standard library + numpy)
* Node 22+ (Stryker 10 requires it)
* JDK 17+ and Maven (a Maven distribution is vendored by the fetch script below)
* MiKTeX or TeX Live with `pdflatex` and `bibtex`
* **No Perl** is required: `latexmk` is deliberately not used

## Reproduce the manuscript

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\build.ps1 -Clean
```

That runs `pdflatex` three times with `bibtex` in between and writes `paper/out/main.pdf`.
It is equivalent to:

```powershell
cd paper
pdflatex --disable-installer main.tex
bibtex main
pdflatex --disable-installer main.tex
pdflatex --disable-installer main.tex
```

### Do not fight the build; these are deliberate

1. **`--disable-installer` is required.** MiKTeX's package installer hangs indefinitely when it cannot
   write to its user data directories.
2. **`\usepackage{lmodern}` in `main.tex` is required.** The official `sbc2025.cls` comments out its
   own `lmodern` load, leaving T1 bitmap fonts, and microtype then aborts with
   *"pdfTeX error (font expansion): auto expansion is only possible with scalable fonts"*.
3. **Do not load `booktabs` or `longtable`.** `tabularray` is loaded by the class and provides the
   rules; `booktabs` redefines `\toprule` and every `tblr` fails with *"! Misplaced \noalign"*.
4. **The bibliography is generated and pure ASCII.** `scripts/make_bib.py` transliterates diacritics
   because BibTeX's `format.name$`/`change.case$` corrupt multi-byte UTF-8.

## Reproduce the numbers

No number in the manuscript is typed by hand. `paper/numbers.tex` is generated from result files:

```powershell
python scripts/make_numbers.py     # paper/numbers.tex  <- data/, results/
python scripts/make_bib.py         # paper/refs.bib     <- refs/verified.csv
python scripts/audit_refs.py       # re-resolves every DOI at Crossref; must print 78/78 PASS
```

If a source file is missing, the corresponding macro renders as a visible `??` sentinel, so a stale or
invented value cannot reach the PDF silently.

## Reproduce the corpus measurements

```powershell
# 1. enumerate the sampling frame (token-free; no GitHub API key needed)
python scripts/enumerate_frame.py

# 2. draw the seeded sample and screen eligibility (streams tarballs; no clones)
python scripts/corpus_screen_tar.py --limit 2100

# 3. attempt a real BDD run for each eligible repository
python pipelines/mutation/build_screen.py --language java      --out data/corpus/bs_java.csv
python pipelines/mutation/build_screen.py --language typescript --out data/corpus/bs_ts.csv

# 4. static drift indicators
python pipelines/metrics/static_metrics.py --repo <owner/name>

# 5. mutation measurement, BDD-only and full-suite
python pipelines/mutation/measure.py --repo <owner/name> --mode bdd
python pipelines/mutation/measure.py --repo <owner/name> --mode full
python pipelines/analysis/combine_metrics.py
python pipelines/analysis/stats.py
```

### Toolchains that are proven to work

| Stratum | Toolchain | Demonstrated result |
|---|---|---|
| JavaScript/TypeScript | Stryker 10.1.1 + `@stryker-mutator/cucumber-runner` 10.1.1 + Cucumber 12.2.0 | 43 mutants, 31 killed, 72.09 %, **0 no-coverage**, per-scenario attribution |
| Java | PIT 1.30.2 + `pitest-junit5-plugin` 1.2.3 + Cucumber-JVM 8.1.0 | 19 mutants, 14 killed, 74 %, **0 no-coverage**, scenarios named individually |

Both harnesses are in `pilot/smoke-js/` and `pilot/smoke-java/` and can be re-run directly.

> **Important environment note.** Stryker and PIT launch piped child processes, which some sandboxes
> forbid (`EPERM: spawn`). The recorded runs were executed with full process control. If you reproduce
> this inside a restricted sandbox, run the mutation stages outside it or in CI.

## Rebuild the bibliography / audit the references

```powershell
python scripts/merge_refs.py        # merge per-facet CSVs into refs/verified.csv
python scripts/refresh_from_crossref.py   # re-derive author/title/venue from Crossref
python scripts/audit_refs.py        # fail loudly if any DOI does not resolve or a title mismatches
```

## Data and ethics

All analysed repositories are public and were used under their own licences, recorded per repository
in the screening tables. No third-party repository source code and no paper PDFs are redistributed
here: both are fetched at run time from their public origins. Repositories without a detectable
permissive licence were excluded before any modification. Mutation analysis modifies code only in
isolated working copies, and seeded-drift experiments are confined to separate copies.

## What this package does **not** contain, and why

* **No human-rater data.** The protocol requires two independent raters for the judgement-coded
  indicators (business-rule relevance, assertion weakening, mirror steps) and a Cohen's kappa. No
  independent rater was available, so none was fabricated, and the paper reports the absence as a
  limitation.
* **No completed build screen.** Only 18 of the 94 eligible repositories were build/execution-tested.
  The paper reports the attempted count and explicitly declines to claim a green-suite *rate*.
* **No longitudinal series.** The history miner requires a full clone with commit history; the
  screened repositories were materialised from source archives, which carry no `.git`. The instrument
  is implemented and shipped, but it is not exercised on real data here, and the paper makes no
  longitudinal claim.

## Citation

See `CITATION.cff`.

## Licence

MIT — see `LICENSE`. The official iSys template files are redistributed only as the venue's own
submission template.

## Three-mode measurement, validation and verification

The first version of this study measured mutation kill in two modes (`BDD`, `FULL`) and defined a
differential metric that was **mathematically inverted**: it reported the uplift of the *non-BDD*
tests as though it were the uplift of the specification layer, so a decorative BDD layer scored
highest. The corrected pipeline runs three modes over one mutant set and is guarded by regression
tests.

```powershell
# Metric definitions + regression tests (decorative / redundant / valuable / BDD-only)
python pipelines/analysis/differential.py            # self-test, exit 0 = identities hold
python -m unittest discover -s tests -v              # same, under unittest

# Three-mode feasibility, Java (PIT reports coverage in every mode -> exact)
python pipelines/mutation/feasibility_java.py --operators aligned
python pipelines/mutation/feasibility_java.py --operators default --mode full   # divergence

# Three-mode feasibility, JS/TS (Stryker; NON_BDD coverage unavailable -> upper bound)
cd pilot/smoke-js
npx stryker run stryker.bdd.json
npx stryker run stryker.nonbdd.json
npx stryker run stryker.full.json

# Join both ecosystems into one report
python pipelines/analysis/feasibility_report.py

# Seeded-drift campaign: inject known drift, re-measure, revert (needs a clean tree)
python pipelines/validation/seeded_drift.py

# Zero-build static census over all eligible repositories (isolated per repo, timeout-guarded)
python pipelines/metrics/census.py --skip-d3 --timeout 45

# Human-rater coding package (kappa is never fabricated)
python scripts/export_coding_sheets.py
python scripts/compute_irr.py --a <raterA.csv> --b <raterB.csv> --label-column business_rule_relevant

# Pre-submission verification gate: one command, one exit code
python tools/verify-submission.py
```

### What is deliberately absent

`scripts/compute_irr.py` exists and is tested, but **no kappa is reported** anywhere in the paper.
Inter-rater reliability is a property of two independent humans; a model coding both sheets measures
self-consistency, not agreement. `docs/coding/RUBRIC.md` carries the rubric and
`docs/AUTHOR-INPUT-NEEDED.md` lists every remaining human-only action.
