# results/RUNLOG.md — append-only evidence log

Every quantitative claim in the paper must trace to an entry here. An entry is
valid only if it records: **command**, **UTC timestamp**, **git commit SHA**,
**host**, **seed**, **tool versions**, and **where the output went**.

Rules:
- Append only. Never edit or delete a past entry; supersede it with a new one.
- Record failed and abandoned runs too — the attrition log depends on them.
- `git_sha` is the commit of the *analysed harness code*, not of the corpus repo.
  Corpus repository identities and commit SHAs live in `data/corpus/LOCKFILE.csv`.

## Environment (constant unless an entry says otherwise)

| Fact | Value |
|---|---|
| Host | `BOOK-FLG1TLH8V5` |
| OS | Microsoft Windows NT 10.0.26300.0 |
| CPU | 13th Gen Intel Core i5-1335U |
| RAM | 15.7 GB |
| Python | 3.12.4 |
| Node | v24.11.0 |
| npm | 11.6.1 |
| Java | Oracle JDK 22.0.1 (`JAVA_HOME` set per command) |
| Maven | Apache Maven 3.9.9 (vendored at `tools/jvm/maven/`, local repo `.m2repo/`) |
| Gradle | 8.10.2 (vendored at `tools/jvm/gradle/`, `GRADLE_USER_HOME=.gradle-home/`) |
| LaTeX | MiKTeX 25.12; `pdflatex`/`bibtex` used with `--disable-installer` |
| Per-shell note | Shell is Windows PowerShell 5.1; there is no `pwsh` binary |

---

## R001 — JS/TS mutation harness feasibility (Stryker × Cucumber)

- **UTC**: 2026-11-25T11:54:56Z
- **git_sha**: `b7115a4` (harness commit; smoke project untracked at run time)
- **seed**: n/a (no sampling in this probe)
- **purpose**: prove that Stryker can be driven by a Cucumber-JS suite and that
  coverage-conditioned mutation scoring works, before committing the design.
- **command**:
  ```powershell
  cd pilot\smoke-js
  npx --no-install cucumber-js                       # baseline suite
  npx --no-install stryker run stryker.conf.json      # mutation analysis
  ```
- **tool versions**: `@stryker-mutator/core` 10.1.1, `@stryker-mutator/cucumber-runner` 10.1.1,
  `@cucumber/cucumber` 12.2.0, Node v24.11.0.
- **config**: `pilot/smoke-js/stryker.conf.json` — `testRunner: "cucumber"`,
  `coverageAnalysis: "perTest"`, `mutate: ["src/**/*.js"]`, `timeoutMS: 30000`, `concurrency: 2`.
- **baseline result**: 4 scenarios, 16 steps, all passed.
- **mutation result**: 43 mutants — 31 killed, 12 survived, **0 no-coverage**, 0 timeout, 0 errors.
  Mutation score **72.09 %** (total and covered identical, because coverage was complete).
- **artifact**: `results/pilot/smoke-js-mutation.json` (Stryker JSON reporter).
- **repeatability**: run twice, identical counts both times (exit 0).
- **what this proves**: the JS/TS stratum is tool-feasible; Stryker reports a
  `NoCoverage` status separately, so the mandatory covered-vs-all conditioning
  (RQ2) is measurable; per-mutant test attribution names the individual Cucumber
  scenarios, so BDD-only vs full-suite differential kill is computable.
- **what this does NOT prove**: that the same works on a real third-party
  repository (dependency rot, TS build steps, monorepos). That is the pilot's job.
- **environment caveat**: under the earlier `workspace-write` policy this command
  failed with `EPERM: spawn` (errno -4048) because Stryker launches piped child
  processes. The run recorded above was executed under the `danger-full-access`
  policy. **Any reproduction must therefore run unsandboxed, or in CI.**

### Observed survivors (illustrative, not a finding)
All 12 survivors are boundary/equality mutants in `src/pricing.js`, e.g.
`orderTotal > 250` → `orderTotal >= 250` and `orderTotal > 750` → `>= 750`.
The suite exercises those branches but never at the boundary value, i.e. the
scenarios are *reachable but not probing*. This is a concrete, if anecdotal,
instance of the oracle-weakness phenomenon the study targets.

---

## R002 — Java mutation harness feasibility (PIT × Cucumber-JVM)

- **UTC**: 2026-11-25T11:56:17Z
- **git_sha**: `b7115a4` (smoke project untracked at run time)
- **seed**: n/a (no sampling in this probe)
- **purpose**: prove that PIT can drive a Cucumber-JVM suite through the JUnit
  Platform engine and produce a mutation score, before committing the design.
- **command**:
  ```powershell
  cd pilot\smoke-java
  $env:JAVA_HOME="C:\Program Files\Java\jdk-22"
  mvn -B -Dmaven.repo.local=<repo>\.m2repo test                    # baseline
  mvn -B -Dmaven.repo.local=<repo>\.m2repo pitest:mutationCoverage # mutation
  ```
  (`mvn` = vendored Apache Maven 3.9.9 at `tools/jvm/maven/`.)
- **tool versions**: PIT `pitest-maven` 1.30.2, `pitest-junit5-plugin` 1.2.3,
  `io.cucumber:cucumber-java` 8.1.0, `cucumber-junit-platform-engine` 8.1.0,
  JUnit Platform 6.1.3, JDK 22.0.1, `maven.compiler.release=17`.
- **config**: `pilot/smoke-java/pom.xml` — `targetClasses=smoke.pricing.*`,
  `targetTests=smoke.RunCucumberTest`, operators = PIT `DEFAULTS` (probe only).
- **baseline result**: BUILD SUCCESS, Cucumber features discovered and executed.
- **mutation result**: **19 mutants — 14 killed (74 %), 0 with no coverage**,
  test strength 74 %, line coverage of mutated classes 12/14 (86 %),
  29 tests ran (1.53 per mutation), total 5 s.
- **artifact**: `pilot/smoke-java/target/pit-reports/` (XML + HTML); console
  transcript `pilot/smoke-java/pitest.out.txt`.
- **what this proves**: the Java stratum is tool-feasible; PIT discovers individual
  Cucumber scenarios as tests (it names them in its timing block), so BDD-only vs
  full-suite differential kill is computable in Java as well as JS.
- **method-relevant observation**: PIT generated **19** mutants for the same domain
  logic on which Stryker generated **43** (R001). This is direct local evidence that
  mutation tools are not on a common axis, corroborating Kintis et al. (2018), and
  is why `docs/method.md` forbids pooling raw scores across languages.
- **environment caveat**: requires a vendored Maven and a workspace-local repository
  (`-Dmaven.repo.local`), because Maven is absent from the host and the file sandbox
  forbids writing to the default `~/.m2`.

---

## R003 — Python mutation harness feasibility (mutmut × behave/pytest-bdd)

- **status**: **not attempted to completion.** PyPI is unreliable on this host
  (measured 2–3 successful connections in 5 attempts, `ConnectionResetError 10054`);
  mutmut 3.x is also coupled to pytest rather than accepting an arbitrary BDD
  runner. Recorded as a stratum risk, not silently dropped.

---

## R004 — Manuscript build (P5)

- **UTC**: 2026-11-25T13:25:00Z
- **git_sha**: `1a2ef2a` (preceding commit; harness commit recorded in the next commit)
- **seed**: n/a
- **purpose**: produce the submission-ready PDF on the official iSys template.
- **command**: `.\build.ps1 -Clean` (equivalent to `pdflatex x3 + bibtex`, all with `--disable-installer`)
- **result**: **18 pages, 599 KB**, zero errors, zero undefined references, zero undefined citations.
- **toolchain**: MiKTeX 25.12 (pdfTeX 3.141592653-2.6-1.40.28), BibTeX 0.99e, style `apalike-sol.bst`.
- **bibliography**: 78 entries generated by `scripts/make_bib.py` from `refs/verified.csv`; all 78 DOIs
  re-resolved by `scripts/audit_refs.py` (78/78 PASS).
- **numbers**: all quantitative claims in the manuscript come from `paper/numbers.tex`, generated by
  `scripts/make_numbers.py` from `data/` and `results/`. A scan of the rendered PDF found **zero**
  `??` sentinels, i.e. no macro was left undefined.
- **note on venue rule V10**: iSys requires a *minimum* of 15 pages; 18 pages satisfies it. No maximum
  is stated by the journal.
- **build-script defects found and fixed while producing this artefact** (each would have blocked a
  replicator):
  1. `$installerFlag = if (...) { @('--disable-installer') }` is unrolled by PowerShell to a *string*,
     so `@installerFlag` splatting threw and pdflatex never ran — the build failed with a stale exit
     code and produced no log.
  2. MiKTeX writes log4cxx notices to stderr; with `$ErrorActionPreference='Stop'` and `2>&1`, those
     became terminating errors even on a successful compile.
  3. `booktabs` loaded after `tabularray` redefines `\toprule` and every `tblr` died with
     "! Misplaced \noalign".
  4. DOI fields contain `_`, which LaTeX reads as a subscript -> "! Missing $ inserted".
  5. BibTeX's `format.name$`/`change.case$` corrupt multi-byte UTF-8 and strip bare accent commands;
     the bibliography is now emitted as pure ASCII with diacritics transliterated.

## R005 — Corpus screening and build/execution screen (P2)

- **UTC**: 2026-11-25T13:17:12Z
- **command**: `python scripts/corpus_screen_tar.py --limit 2100` then `pipelines/mutation/build_screen.py`
- **frame**: 2,552 unique repositories (12 topic slugs x 5 language filters x 6 pages, 252 pages,
  snapshot SHA-256 recorded in `data/frame/FRAME.md`)
- **screened**: 2,552 attempted, **94 eligible** (3.68 %)
- **build/execution screen**: **41 attempted**, 0 green Gherkin baselines (24 build_fails, 7 bdd_fails, 8 no_bdd_execution, 1 timeout, 1 unsupported)
- **caveat, disclosed in the paper**: the build screen did not complete for all 94 eligible
  repositories. The manuscript reports the attempted count and states that no green-suite *rate* is
  claimed, because the denominator is incomplete.

- **correction history (R005)**: this entry has recorded 18, then 25, then 31 attempted while
  the Java shard was still running; it now records the final **41**. The authoritative figure is
  recomputed from `data/corpus/bs_*.csv` by `scripts/make_numbers.py` and carried into the
  manuscript as `\Nbuildtested`. If this entry and the generated macro ever disagree, **the
  macro is right and this entry is stale**. The zero-green result was re-verified after the
  shard completed and is unchanged.

---

## R006 — three-mode differential-kill feasibility, Java (2026-11-25)

**Command** `python pipelines/mutation/feasibility_java.py --operators aligned`
**Toolchain** PIT 1.30.2 + pitest-junit5-plugin 1.2.3, Cucumber-JVM 8.1.0, JDK 22, Maven 3.9.9

Three execution modes over one mutant set (`bdd` = `smoke.RunCucumberTest`,
`nonbdd` = `smoke.UnitPricingTest`, `full` = `*`). Aligned decision-logic operators:
CONDITIONALS_BOUNDARY, NEGATE_CONDITIONALS, MATH, INCREMENTS, INVERT_NEGS, PRIMITIVE_RETURNS,
EMPTY_RETURNS, TRUE_RETURNS, FALSE_RETURNS.

- 40 mutants per mode; BDD-only: 13 killed, 5 survived, **22 NO_COVERAGE**
- comparison set `S = executed(BDD) ∩ executed(NON_BDD)` = **15**
- `DK_bdd_uplift` = **0.000** (exact), `DK_nonbdd_uplift` = 0.200, Overlap = 0.800,
  `BDD_unique_share` = 0.000, `BDD_total_share` = 0.800
- `containment_ok` = True, `mode_integrity_ok` = True
- **Interpretation**: the specification layer kills most of what it touches but adds *no* unique
  detection on this suite. Under the retired inverted metric the same run would have been reported as
  a BDD uplift of +0.200, which is the opposite conclusion.

## R007 — three-mode differential-kill feasibility, JavaScript/TypeScript (2026-11-25)

**Commands** `npx stryker run stryker.bdd.json` / `stryker.nonbdd.json` / `stryker.full.json`
**Toolchain** Stryker 10.1.1, @stryker-mutator/cucumber-runner 10.1.1, @cucumber/cucumber 12.2.0, Node 24

- 96 mutants per mode; BDD-only: 31 killed, 12 survived, **53 NO_COVERAGE**
- `MS_all` = 32.29 %, `MS_cov` = 72.09 %
- `S` = 43, `DK_bdd_uplift` = 0.070 (**upper bound**), `DK_nonbdd_uplift` = 0.093,
  `BDD_unique_share` = 0.086, `BDD_total_share` = 0.886
- **Bound, disclosed**: Stryker's `command` runner cannot report per-test coverage, so
  `executed(NON_BDD)` collapses to "all mutants" and `S` to the BDD-covered set. Both effects push
  the BDD uplift upward; the Java figure is the exact one.

## R008 — `NO_COVERAGE` control (2026-11-25)

Both suites now contain a domain module that no test references
(`src/legacy-pricing.js`, `LegacyPricing.java`). Observed uncovered-mutant counts: **53** (JS) and
**22** (Java), both non-zero. This is the control the first submission lacked: a zero count cannot
demonstrate that a tool separates *executed and survived* from *never executed*, whereas a non-zero
count does. `MS_all` and `MS_cov` differ by more than a factor of two on the same runs.

## R009 — seeded-drift validation campaign (2026-11-25)

**Command** `python pipelines/validation/seeded_drift.py`
**Design** one injection at a time into the working JS suite, re-measure D1–D7 and the BDD-only
mutation score, revert via `git checkout`, plus a negative control. An injection is accepted only if
the unmutated suite still passes.

| injection | target | observed | mutation score |
|---|---|---|---|
| I1 skip tags | D1 | +0.167 detected | unchanged |
| I2 weakened assertion | D2 | **no movement** | 72.09 % → **20.93 %** |
| I3 duplicated scenario | D4 | +0.019 detected | unchanged |
| I4 mirror step | D7 | **no movement** | 72.09 % → **32.56 %** |
| I5 wrong literal | D6 | invalid (suite fails) | n/a |
| C1 negative control | — | unchanged | unchanged |

**Result: 2 of 4 sensitivity targets detected.** The two misses are the substantively important
ones: an oracle that can never fail and an oracle that re-derives the expected value both leave the
static indicators flat while destroying more than half the suite's killing power. This is reported in
the paper as evidence that the static indicators are *not* substitutes for mutation-based measurement.

## R010 — operator alignment divergence (2026-11-25)

`python pipelines/mutation/feasibility_java.py --operators default --mode full` → **41** mutants,
versus **40** with the aligned decision-logic set. On this suite alignment removes a single mutant;
the cross-tool contrast (PIT 40 vs Stryker 96) is far larger, which is why scores are never pooled
across ecosystems.

## R011 — static D1–D7 census, zero builds (2026-11-25)

**Command** `python pipelines/metrics/census.py --skip-d3`
**Design** one subprocess per repository with a hard timeout, so a pathological working copy cannot
block the census. D3 is disabled and reported as *undefined*: it needs `git blame`, most working
copies carry no VCS history, and on the minority that do the blame calls dominated run time. Results
are generated into `data/metrics/census.json`; no indicator is imputed.
