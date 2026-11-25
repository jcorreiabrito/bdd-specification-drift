# docs/DEVIATIONS.md — deviations from the brief and from `docs/method.md`

**Purpose.** The operating contract requires that any deviation from `docs/method.md` after the P1
gate be logged here with a reason and a timestamp, and disclosed in the paper. This file also records
**constraints imposed by the environment** that force a departure from the original plan, because the
paper must disclose those too even though they are not "method changes" in the narrow sense.

**Status: the P1 gate has NOT closed.** No corpus has been measured, so no post-gate deviation can
yet exist. Everything below is either (a) an environment-forced constraint discovered during P0–P1.5,
or (b) a pre-gate decision awaiting human approval.

---

## A. Environment-forced constraints (must be disclosed in the paper)

| # | Plan said | What actually happened | Reason | Consequence for the paper |
|---|---|---|---|---|
| **E1** | Use the GitHub API with a token; cache responses under `data/raw/` | **No token was available.** Unauthenticated REST is 60 req/h and was already exhausted | Token never supplied; the brief assumed one | The sampling frame is enumerated from public GitHub **topic pages** (token-free, 252 pages, snapshot-hashed) instead of code search. The frame is therefore *"repositories that adopted at least one declared BDD-related topic tag on the snapshot date"*. **Topic-tagging bias must be stated as a threat to external validity.** |
| **E2** | Per-repo build/run harness with isolated builds | **Docker is absent from the host**; only JDK 22 is installed; Maven and Gradle are absent | Host capability | No build isolation. Java corpora targeting 8/11/17 may fail on JDK 22 and are categorised `tool_incompatibility`, distinct from `dependency_rot`. Cross-repo toolchain contamination is a live threat, mitigated by per-repo cache localisation plus a repeatability probe (method §14 T10). Maven 3.9.9 and Gradle 8.10.2 were **vendored into the repository** to make the Java stratum possible at all. |
| **E3** | Mutation tools drive the BDD runner | **Tools cannot run under the file sandbox**: Stryker failed with `EPERM: spawn` (errno −4048) under `workspace-write` | Sandbox forbids piped child processes by design | All mutation runs execute unsandboxed or in CI. Disclosed so that reproduction is realistic. Recorded in `results/RUNLOG.md` R001. |
| **E4** | Three language strata: Java, JS/TS, Python | **Python stratum not established.** PyPI resets connections (2–3 of 5 attempts); mutmut 3.x is coupled to pytest and does not accept an arbitrary BDD runner | Network filtering + tool design | Python is reported as `at risk`, not silently dropped (RUNLOG R003). If it cannot be established, Python is dropped as a stratum and **reported as a limitation**, per the brief. |
| **E5** | `latexmk` build via `build.ps1` | `latexmk` is unusable; the official `sbc2025.cls` omits `lmodern` and microtype dies on bitmap fonts; the MiKTeX installer hangs under the sandbox | No Perl; class defect; sandbox | `build.ps1` was written from scratch: `pdflatex --disable-installer` ×3 + `bibtex` with `apalike-sol.bst`, and the document must load `\usepackage{lmodern}`. Documented in `build.ps1` header and `submission/VENUE-RULES.md`. |
| **E6** | Reference engine = biber/bibtex as convenient | **BibTeX only**, with the venue's `apalike-sol.bst` (APA) | The iSys template ships a BibTeX `.bst`, not a biblatex style | Reference formatting is dictated by the venue template, not by preference. |
| **E7** | Shadow libraries excluded (per brief) | Enforced: no shadow library was used. Paywalled work was reached via open-access copies, institutional repositories, Wayback replays of abstracts, or not at all | Brief + integrity rule | Several works are cited from **abstracts only** (notably Zampetti et al. 2020), and each such work is marked `crossref+abstract` in `refs/verified.csv`. The paper must not over-claim from abstract-only sources. |

## B. Pre-gate findings that change the design, pending human decision

| # | Finding | File | Awaiting |
|---|---|---|---|
| **G1** | iSys is an **Information Systems** journal; a pure SE mutation-testing paper is at high desk-rejection risk. Options: reframe as IS/DSR, submit as-is, or change venue. | `submission/VENUE-RULES.md` V2–V5; `docs/GATE-1.5-REPORT.md` §2 | **D1** |
| **G2** | Pilot yield is **5.3 %** (95 % CI 2.8–9.8 %); the eligible set is dominated by BDD **tooling** repositories, not applications with a domain layer, so the "mutants as business-rule proxy" construct is threatened. | `data/pilot/PILOT.md`; gate report §5.1 | **D2, D3** |
| **G3** | `"specification drift"` is **not** an established term; the paper must coin and define it as a specialisation of architectural drift, with hedging. | `lit/novelty.md` §5 | naming decision, gate report §1 |
| **G4** | Novelty survives only as a **conjunction**; AAT4IRS (2024) already mutation-tested a BDD suite once. | `lit/novelty.md` | acknowledgement in the introduction |


## C. Post-gate deviations

The P1.5 gate was approved with two decisions (D1: reframe as IS/Design-Science; D2: redefine the frame
to require a licence and an application shape). Execution then departed from `docs/method.md` in the
following respects. Each is disclosed in the manuscript.

| # | Deviation | Reason | Disclosed in |
|---|---|---|---|
| **G5** | `docs/method.md` was **not frozen or externally registered**. It is described in the paper as *pre-specified*, not pre-registered. | No registration was lodged and the document was edited as the pilot exposed problems. Claiming pre-registration would be false. | `paper/sections/05-method.tex` opening; threats |
| **G6** | Eligibility criteria E7/E8 (framework-exclusion list + domain-layer test) were replaced by an observable application-shape test. | The original tests were not mechanically decidable without a build, and admitted tooling that passed them. | `05-method.tex` §Eligibility; threats |
| **G7** | The seeded-drift validation campaign was **not performed**. | Pilot yielded no repository with a green Gherkin baseline, so there was no suite to inject drift into. | `08-threats.tex`; `docs/PROTOCOL.md` §8 |
| **G8** | Inter-rater reliability was **not performed**; no Cohen's kappa is reported. | No independent human raters were available. No automated labeller was substituted. | `08-threats.tex`; abstract limitation sentence |
| **G9** | The longitudinal component was implemented but **not exercised on real data**. | Repositories were materialised from source archives and depth-one clones, which carry no history to walk. | `06-results.tex`; `08-threats.tex` |
| **G10** | The build/execution screen covered 25 of the 94 eligible repositories, not all. | Wall-clock cost of dependency installation and Maven resolution. | `06-results.tex` §Build and execution screen |
| **G11** | Four artefacts mandated by `docs/method.md` §5.4/§15.1/§15.3 were **not produced**: `results/runlog.jsonl`, `scripts/render_runlog.py`, `data/corpus/LOCKFILE.csv`, `data/attrition/attrition.csv`. The run log is Markdown (`results/RUNLOG.md`) and the attrition data lives in `data/corpus/bs_*.csv`. | The Markdown log and the per-language CSVs carry the same information in a different shape; the JSONL/LOCKFILE forms were not generated. A replication should generate them. | replication `README.md` |
| **G12** | Python stratum not established. | PyPI resets and `mutmut` 3.x couples to pytest rather than a BDD runner. | `06-results.tex`; `results/RUNLOG.md` R003 |

**Note on G11.** This is recorded rather than quietly satisfied because the method document names those
paths. A reader comparing the protocol to the package will find the information, but not at the named
paths; that mismatch is a defect in the package's conformance to its own protocol, not a missing
measurement.


---

## D. Revision round 2 — peer-review remediation (2026-11-25)

This section records every change to the protocol made in response to the first round of peer
review, with the reason. Each entry is a deviation from the earlier protocol as written, not a
silent improvement.

| # | What changed | Reason | Where reflected |
|---|---|---|---|
| **G13** | **The differential-kill metric was mathematically inverted and is replaced.** The first submission defined `DK_norm = MS_cov(FULL,S) − MS_cov(BDD,S)` and described it as the uplift *of* the specification layer. That quantity is the uplift of the *non-BDD* tests: it is maximal when BDD kills nothing and zero when BDD is the only thing detecting a fault. Replaced by a three-mode decomposition (BDD / NON_BDD / FULL) with `DK_bdd_uplift`, `DK_nonbdd_uplift`, `Overlap`, `BDD_unique_share` and `BDD_total_share`, all on `S = executed(BDD) ∩ executed(NON_BDD)`. | A peer reviewer identified the inversion; the two worked counter-examples in `pipelines/analysis/differential.py` reproduce it. Leaving it would have inverted the paper's headline interpretation. | `05-method.tex` §5.4; `07-discussion.tex`; `docs/PROTOCOL.md` §4; `pipelines/analysis/differential.py`; `tests/test_differential.py` (21 tests) |
| **G14** | A third execution mode, `NON_BDD`, was added to the harness. Previously only `BDD` and `FULL` existed. | Two modes cannot attribute detection: the BDD uplift requires subtracting the non-BDD kill set, which was never measured. | `pilot/smoke-js/stryker.{bdd,nonbdd,full}.json`; `pipelines/mutation/feasibility_java.py` |
| **G15** | A deliberately unexercised domain module was added to both feasibility suites, so `NO_COVERAGE > 0` is now empirically observed. | The first submission reported zero uncovered mutants and argued the zero proved the harness could separate execution from non-execution. A reviewer correctly noted a zero proves nothing: the suites simply covered everything. | `pilot/smoke-js/src/legacy-pricing.js`; `pilot/smoke-java/.../LegacyPricing.java`; `06-results.tex` §6.4 |
| **G16** | PIT operator names corrected, and an aligned decision-logic set is now used for the primary runs. `RETURN_VALS`, `BOOLEAN_TRUE_RETURN` and `BOOLEAN_FALSE_RETURN` are not valid in PIT 1.30.2; the accepted names are `PRIMITIVE_RETURNS`, `EMPTY_RETURNS`, `TRUE_RETURNS`, `FALSE_RETURNS`. The invalid list caused PIT to generate **zero** mutants, which would have been misread as "nothing to mutate". | Discovered while executing the feasibility re-run; recorded because a wrong operator name silently produces an empty measurement rather than an error in the results. | `pipelines/mutation/feasibility_java.py`; `06-results.tex` §6.4 |
| **G17** | The seeded-drift validation campaign was executed. Result: **2 of 4** sensitivity targets detected, 1 injection invalid, negative control clean. The two misses are `D2` (weakened assertion) and `D7` (mirror step); in both, the BDD-only mutation score fell by more than half while the target indicator did not move. | The campaign was skipped in the first submission, leaving indicator sensitivity unvalidated. The honest result is that the static indicators have false negatives, which is now stated rather than implied. | `pipelines/validation/seeded_drift.py`; `06-results.tex` §6.5; `data/metrics/seeded_drift.json` |
| **G18** | The static D1–D7 census was run over all statically eligible repositories, **with D3 disabled**. | The first submission omitted the census entirely although it needs no builds. D3 requires `git blame`; most working copies were materialised from source archives and carry no history, and on the minority that do the blame calls dominated run time by orders of magnitude. D3 is therefore reported as undefined, with the reason, rather than imputed. | `pipelines/metrics/census.py`; `06-results.tex` §6.6; `data/metrics/census.json` |
| **G19** | The traceability-coverage measure is **defined but not measured**, and the manuscript no longer claims the instrument includes a traceability measurement. | A reviewer noted that §3.5 claimed a measure that no result used. Identifying business rules reliably needs human coding of repository documentation, which was not performed. The subsection is now explicit motivating background. | `03-related.tex` §3.5 |
| **G20** | Build and execution screening remains **single-host and not containerised**. No Docker, Podman or nerdctl was available in the execution environment. | The reviewer asked for multi-runtime containerised screening of 100 % of eligible repositories. That is not achievable without a container runtime, and running it anyway would confound ecosystem attrition with JDK/Node availability on one machine. Recorded as a threat rather than papered over. | `08-threats.tex` §8.8, §8.11; `docs/AUTHOR-INPUT-NEEDED.md` H7 |
| **G21** | The human-rater coding package was exported (blinded sheets, rubric, κ script). **No κ is reported.** | Inter-rater reliability requires two independent humans. No model was substituted, because a model coding both sheets measures self-consistency, not agreement. | `docs/coding/RUBRIC.md`; `scripts/export_coding_sheets.py`; `scripts/compute_irr.py`; `docs/AUTHOR-INPUT-NEEDED.md` H1 |
| **G22** | The longitudinal Theil–Sen miner remains **implemented but not exercised** on corpus history. | It requires full-history clones. The institutional archive path caps payload size and the environment had no authenticated API access, so full clones for the eligible set were not obtained in this round. | `docs/AUTHOR-INPUT-NEEDED.md` H6 |
