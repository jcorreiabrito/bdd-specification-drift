# `docs/method.md` — Pre-registered protocol

**Study.** *Do Public BDD Suites Still Work as Oracles? A Mutation-Based Study of Specification Drift in Cucumber-Style Test Suites*

**Document.** `docs/method.md`, P1 pre-registration, v1.0-draft, 2026-11-25 (UTC−03:00), role S2 (methodologist). **DRAFT — frozen only at the human P1 gate, before any collection.** Freeze artefact: SHA-256 of this file → runlog entry `prereg-freeze` in `results/RUNLOG.md`, and the OSF deposit permitted by venue rule V21. Binding inputs: `docs/RESEARCH_PROTOCOL.md`, `TEAM.md` §3 (measured environment), `submission/VENUE-RULES.md`. **Snapshot date 2026-11-25**: all enumeration, clone, age and churn computation is relative to it. Markers: `[GATE-DECISION]` human must ratify · `[PILOT-DERIVED]` fixed after P1.5 · `[P3-DERIVED]` computed during measurement · `[CITE: …]` S1 must supply a verified reference. After freeze, changes only via `docs/DEVIATIONS.md` (§16).

## 1. Study design overview

**1.1** Observational, non-experimental, one corpus, two components: **cross-sectional** (RQ2, oracle strength at HEAD) and **longitudinal** (RQ3, drift accumulation over the repository's own history). No treatment is assigned; no repository is modified. **The design cannot establish causality.** It establishes reproducible measurement, the distribution of oracle strength in a defined frame, indicator–strength association, and accumulation over history. Wording is always "associated with", never "causes"/"reduces"/"degrades".

**1.2 Constructs — defined once, used identically everywhere.**

| Construct | Definition | Not this |
|---|---|---|
| **Oracle strength** | Share of *domain-layer mutants* killed by the **BDD-only** run, conditioned on mutant coverage (`MS_cov_bdd`, §7.1). A **snapshot property** of one commit. | A property of time; the full-suite score; a quality judgement of developers. |
| **Drift** | Either (a) a **change over time** in specification artefacts or in oracle strength (measured only in §13), or (b) a **static indicator at one commit** hypothesised to be associated with weaker oracles (§7.4). | A HEAD mutation score is **not** drift. A static indicator is **not** evidence of change; it is a state that predicts weakness. |
| **Mutant** | A synthetic single-operator change to domain-layer code. Generic code mutants are a **PROXY** for business-rule changes; the word *proxy* is mandatory wherever mutants stand in for business rules. | A business-rule change. Its validity is measured (§9, §10.3), never assumed. |

A low HEAD score is never "a drifted suite"; the phrasing is "weak oracle at HEAD" or "drift-indicator-positive".

**1.3 Unit of analysis** = the **repository** (one row per repo). Mutants, scenarios and step definitions are instruments *within* a repo, never independent observations; `n` always counts repositories.

**1.4 RQs as falsifiable claims.** **RQ1 (measurement validity)** — an indicator is valid only if (a) re-running the pipeline on the same SHA reproduces the value exactly (syntactic) or within ±0.02 (parser-dependent), (b) its judgement-coded component reaches Cohen's κ ≥ 0.61, and (c) §10 seeded-drift detection reaches sensitivity ≥ 0.80 and specificity ≥ 0.90. Failing (c) is a **published result** about measurability, not grounds to redefine the indicator. **RQ2 (oracle strength)** — estimation, no significance test: `MS_cov_bdd`, `MS_all_bdd`, `MS_cov_full`, `DK_norm` with 95 % bootstrap CIs, per stratum and overall. **RQ3** — two confirmatory tests (§12.2) plus descriptive longitudinal statistics (§13).

## 2. Sampling frame

**2.1** The frame is a **reproducible enumeration at a stated snapshot date**, never a search ranking. `stars` serves only as an eligibility disjunct (§3 E6) and a covariate. All channels are token-free; GitHub REST is used nowhere, its 60 req/h unauthenticated quota being unable to support a frame.

**2.2 Channels.**
**C1** `https://github.com/topics/<slug>?l=<lang>&o=desc&s=stars&page=<p>` (stars-descending).
**C2** the same with `s=updated` (updated-descending) — required so recent low-star repositories, which E6 admits, can enter.
**C3** repository-search HTML `https://github.com/search?q=topic%3A<slug>&type=repositories` — *attempted only*; a login/JS shell or non-200 is recorded as unavailable and the frame rests on C1–C2.
`scripts/probe_gh_surfaces.py` encodes the C1/C3 probes; its verbatim P2 output goes to `data/frame/probe/` with HTTP status and body SHA-256.

**2.3 Grid** = full cross product `T × L × Ω × Π`.
`T`, fixed before enumeration, in this order: `cucumber`, `bdd`, `gherkin`, `cucumber-jvm`, `behave`, `pytest-bdd`, `cucumber-js`, `bdd-framework`, `living-documentation`, `acceptance-testing`.
`L` = `java`, `javascript`, `typescript`, `python`; a repo found under several filters is kept once and its analysis language comes from the step-definition census (§4.2), not the filter.
`Ω` = `stars`, `updated`; `Π` = pages `1..10` (`P_max = 10`, design constant).

**2.4 Procedure.** (1) Fetch every cell sequentially, 1.5 s politeness delay, the UA string already in `scripts/probe_gh_surfaces.py`; record `http_status`, `content_sha256`, `enumerated_utc`, `bytes`. (2) Extract `/owner/name` links inside `<article>` cards with a parser validated once against a hand-counted page. (3) Stop paginating a cell at the first of: zero **new** repo ids, HTTP 404, `p > P_max`; record `stop_reason`. (4) **Degenerate-cell test** — degenerate if its repo-id list equals another cell's of the same `(t, l)` after ordering, i.e. `o`/`s` were ignored; dropped and logged. (5) De-duplicate on `repo_id = lower(owner/name)`; frame membership = appearance in ≥ 1 non-degenerate cell. (6) Write `data/frame/frame.csv`:

```
repo_id,owner,name,url,first_cell_id,all_cell_ids,n_cells,stars_shown,description_shown,primary_language_shown,enumerated_utc,html_sha256,frame_version
```

(7) Freeze: `N_frame` and `frame_sha256` in `data/frame/frame.json`.

**2.5 Frame size.** `N_frame` is **not** stated here: it is a property of GitHub on 2026-11-25, unknowable before enumeration, and inventing it would violate `docs/RESEARCH_PROTOCOL.md` §1.3. The protocol fixes the procedure and the value's location — `data/frame/frame.json:N_frame`, quoted in the paper. Minimum viability **≥ 150** repositories, else the pre-registered **extension ladder** runs in order, each version re-frozen with its own hash: **E1** add standby slugs `serenity-bdd`, `specflow`, `scenario-outline`, `step-definitions`, `acceptance-criteria`; **E2** extend `Π` to 20; **E3** replace `L` with `L = {all}` per slug. The frame used is the first version meeting 150; if none does, the study proceeds on the largest frame and the shortfall is a reported limitation.

**2.6 Random draw, fixed seed.** Seed = **`20261125`**. The draw is a **hash-ordered permutation**, not a PRNG call, so any third party reproduces it from `frame.csv` alone:

```
order_key(repo_id) = SHA-256("20261125:" + repo_id)     # hex, lowercase
draw_order         = frame sorted ascending by (order_key, repo_id)
```

`data/frame/draw.csv` stores `i = 1..N_frame`. No re-draw, no resampling; ties break on `repo_id`. `random.sample` depends on RNG implementation; a hash ordering does not.

**2.7 Order and stopping.** Process strictly in `draw_order`; stop at **40** `included` (buffer above the analysis target of 30) or when the draw is exhausted. Because the order is a random permutation, the touched prefix is itself a random sample of the frame, so the §6 attrition rate is unbiased for the frame. Untouched draws are **not** in the attrition log and not in its denominator; the paper says so.

## 3. Eligibility criteria

**3.1 Final rule (E1–E8).** Checked in order; the first failure sets the outcome.

| ID | Criterion | Exact check |
|---|---|---|
| **E1** | Public, cloneable | `git clone --depth 1` exits 0 within 600 s; `git rev-parse HEAD` yields 40-hex |
| **E2** | Licence permits analysis | SPDX from `LICENSE*`/`COPYING*` or the `license` field of `package.json`/`pom.xml`; accepted = {Apache-2.0, MIT, BSD-2-Clause, BSD-3-Clause, ISC, MPL-2.0, EPL-1.0/2.0, GPL-2.0/3.0, LGPL-2.1/3.0, Unlicense, CC0-1.0}; absent or outside ⇒ `excluded / ineligible_no_licence` |
| **E3** | ≥ 1 `*.feature` and **≥ 20 scenarios** | canonical Gherkin parse (§3.3); a `Scenario Outline` counts as **1**, so the count is independent of example-table size |
| **E4** | Step definitions in Java, JS/TS or Python, matched by the repo's own tool | ≥ 1 step-def file (`\.(java\|kt\|js\|ts\|mjs\|cjs\|py)$`) under a step-definition directory, and ≥ 1 *matched* step in the dry run |
| **E5** | Build config runnable without Maven/Gradle | in-repo `mvnw`/`gradlew` **or** `package.json` with `scripts.test` plus a lockfile **or** pytest config; global `mvn`/`gradle` never used (absent on host) |
| **E6** | Active **or** notable | `HEAD` committer date ≥ `snapshot − 24 months` **OR** `stars ≥ 30`; either disjunct suffices |
| **E7** | Application under test, not BDD tooling | fails if `owner/repo` ∈ fixed framework allowlist (`cucumber/*`, `gherkin`, `behave`, `pytest-bdd`, `cucumber-js`, `serenity-bdd`, `karate`, `specflow`, `bdd-*` runners) **or** the description matches `(?i)\b(template\|boilerplate\|example\|sample\|demo\|tutorial\|course\|exercise\|workshop\|starter\|playground\|learning\|cheat ?sheet\|practice)\b`; borderline cases adjudicated per §11, label written to `attrition.csv` |
| **E8** | Domain layer identifiable | §7.5: ≥ 1 domain file **and** ≥ 20 mutants in the dry mutation run. Applied after the build, so a late exclusion |

**3.2 Freeze rule.** E1–E8 are frozen at the P1 gate; afterwards no criterion may be added, relaxed, reinterpreted or applied selectively, and any need becomes a deviation (§16). A criterion the pilot proves unimplementable is **simplified before the gate** and recorded in the gate report, not as a deviation.

**3.3 One Gherkin parser for all strata.** Counts come from a single engine, `@cucumber/gherkin` (npm; the registry is reliable on this host), for every language, so they cannot depend on the repo's own tool version. Where the repo's dry run also reports counts, agreement goes to `attrition.csv:gherkin_agreement` (`exact` / `differs:<n>`); a > 5 % scenario discrepancy triggers manual inspection, and parsed counts are used.

## 4. Strata

**4.1** Strata are `(language, mutation tool, BDD runner)` triples, assigned from the step-definition file census, not the frame filter.

| Stratum | BDD runner | Mutation tool | Build | Config channel |
|---|---|---|---|---|
| **J-Java** | Cucumber-JVM (JUnit 4/5 or Serenity) | PIT via `pitest-maven` | `mvnw`/`gradlew` | CLI `-D` properties; **no `pom.xml` edit** |
| **J-JS** | `@cucumber/cucumber` | Stryker 10.1.1 | `npm ci` | harness-written `stryker.conf.json`, declared as harness artifact |
| **J-PY** | `pytest-bdd` or `behave` | mutmut 3.x | per-repo venv | CLI/config, dumped to runlog |

**4.2 Mixed repos.** Assigned to the language holding the plurality of step-definition files; ties break on plurality of *matched step invocations*, then alphabetically. Both counts recorded; measured **only** in the assigned stratum (no second row: avoids pseudo-replication), the other language still contributing to counts.

**4.3 Stratum drop rule** — empirical, pre-registered, applied after the P1.5 pilot with ≥ 10 repos attempted and ≥ 3 per stratum. A stratum is dropped from confirmatory analysis if any holds: **DR1** < **8** repositories measurable end-to-end; **DR2** the tool cannot emit **per-mutant coverage status**, so §7.2 cannot be computed; **DR3** the §8.6 mode-integrity assertion fails for **≥ 50 %** of attempts; **DR4** (Python) if PyPI unreachability (2–3 of 5 attempts) or mutmut 3.x's pytest coupling makes `behave` repos unrunnable, J-PY narrows to `pytest-bdd` and is dropped entirely if < 8 `pytest-bdd` repos survive. Dropped strata are reported **descriptively** only and excluded from the confirmatory model; the paper states the restriction. A stratum is never replaced by a different tool mid-study.

**4.4 `[GATE-DECISION]`** J-PY is expected to be at risk. Recommended: pre-register it as **at risk** and treat the paper as a two-stratum study (J-Java, J-JS) that *additionally reports* measurable Python repos. Alternative: drop J-PY from the frame — better internal validity, weaker multi-language claim.

## 5. Per-repo funnel and attrition log

**5.1 Stages.** S0 frame membership (§2.4) → S1 clone, `pushed_at` from `git log -1 --format=%cI` → S2 licence (E2) → S3 static BDD screen (E3, E4, §3.3) → S4 tooling gate (E5–E7) → S5 dependency resolution + compile → S6 BDD-only dry run then real run → S7 FULL-suite run (the repo's own canonical command) → S8 domain layer (E8) + mutant generation → S9 mutation, both modes → S10 metrics + git history. The first failing stage sets `outcome`, `reason_category`, `stage_at_failure`.

**5.2 Reason categories.** Exactly one of the eight failure categories — `service_dependency`, `browser_required`, `database_required`, `dependency_rot`, `timeout`, `no_domain_layer`, `tool_incompatibility`, `other` — or, for eligibility failures, one `ineligible_*` value (`unavailable_at_clone`, `no_licence`, `insufficient_scenarios`, `no_stepdefs`, `language`, `no_build_config`, `is_tool_or_template`, `stale_and_low_stars`). `other` **requires** `reason_detail` ≤ 160 chars; an `other` without detail fails the log build. Assignment rules so two coders agree: a dependency version that no longer resolves ⇒ `dependency_rot`; a required JDK/tool version absent on this host ⇒ `tool_incompatibility`; a hang past the stage cap ⇒ `timeout`; failure only because a server/port/container is expected ⇒ `service_dependency`; only a browser driver ⇒ `browser_required`; only a database ⇒ `database_required`. When two apply, the **earliest-stage** cause wins and the second goes in `reason_detail`.

**5.3 Dry-run first.** S6 attempts the tool's dry-run mode first (`--dry-run`, `cucumber.execution.dry-run=true`, behave's dry run), needing no services and no network, yielding the scenario/step/tag inventory, step-definition matching (undefined/ambiguous steps) and the executed-scenario identifier list. The real run proceeds only if the dry run succeeds; this makes S3–S4 verifiable by the repo's own engine and limits build-attrition damage to the metric set.

**5.4 `data/attrition/attrition.csv` — this log **is** the attrition dataset.** Header exactly:

```
repo_id,outcome,stage_at_failure,reason_category,reason_detail,draw_index,frame_cell_ids,first_seen_utc,
licence_spdx,stars_at_snapshot,pushed_at,repo_created_at,primary_language,build_system,wrapper_present,
bdd_tool,bdd_tool_version,feature_file_count,scenario_count,static_outline_count,stepdef_file_count,
stepdef_language_census,matched_step_count,domain_tier,domain_file_count,needs_service,needs_browser,
needs_db,git_head_sha,clone_utc,clone_seconds,build_seconds,bdd_run_seconds,full_run_seconds,
mode_integrity_ok,gherkin_agreement,harness_version,touched_by,run_id,evidence_path,notes
```

`outcome ∈ {included, excluded, failed_to_build, failed_to_measure}`; `evidence_path` points to `results/logs/<repo_id>/`. Rows are append-only: a re-attempt appends a row with the same `repo_id` and a later `run_id`, and the analysis uses the **last** row per repo (fixed here to prevent choosing the favourable attempt).

**5.5 Reported funnel.** Per stratum and overall: `N_frame → touched → cloneable → eligible → built → bdd_run → full_run → measured`, i.e. the counts `included / excluded / failed_to_build / failed_to_measure` with the full category breakdown. No percentage without its denominator.

## 6. Attrition analysis

**6.1** Contrast `included` vs (`excluded` ∪ `failed_to_build` ∪ `failed_to_measure`), and secondarily `included` vs `failed_to_build` alone — the dangerous contrast, because build failure may correlate with suite sophistication.

**6.2** Variables: stars (frame HTML), repo age (`repo_created_at`→snapshot), size (`domain_file_count`, `feature_file_count`, `stepdef_file_count`), scenario count (Gherkin parse, available pre-build for every touched repo), last-commit recency (`pushed_at`) — compared with Mann–Whitney U, median difference and Cliff's δ with bootstrap CI. Language (step-def census) with χ²/Fisher and Cramér's V.

**6.3 Bounding the primary estimate.** Because attrition is non-random, the RQ2 estimate carries a **worst-case bound**: recompute the mean `MS_cov_bdd` assigning every unmeasured repo (a) the 10th and (b) the 90th percentile of the included distribution, quoting the interval beside the included-only estimate, labelled a *bound*, never an estimate. A second sensitivity assigns unmeasured repos the score predicted from §6.2 covariates by multiple imputation (20 imputations, seed `20261125`), assumptions stated.

**6.4 Output.** `results/attrition-analysis.md`: comparison table, bounds, and one paragraph on the **direction** of the plausible bias. The paper's limitations quote the direction, not merely the presence, of attrition.

## 7. Metrics

Notation: for repo `r`, `M` = generated domain-layer mutants; `K ⊆ M` killed; `Cov ⊆ M` covered by the run in question.

**7.1 Outcome: oracle strength.** From the tool's **per-mutant status**, never its summary line — the three tools disagree on what their headline means. `data/tooling/status-map.csv` maps each vocabulary to `{KILLED, SURVIVED, NO_COVERAGE, TIMEOUT, INVALID}`; `INVALID` = non-viable / compile-error / run-error / ignored.

```
MS_all(mode) = (|KILLED|+|TIMEOUT|) / (|KILLED|+|SURVIVED|+|TIMEOUT|+|NO_COVERAGE|)
MS_cov(mode) = (|KILLED|+|TIMEOUT|) / (|KILLED|+|SURVIVED|+|TIMEOUT|)
mutant_coverage(mode) = (|KILLED|+|SURVIVED|+|TIMEOUT|) / (… + |NO_COVERAGE|)
```

`mode ∈ {bdd, full}`; **`MS_cov_bdd` is the primary outcome**; `MS_all_bdd`, `MS_cov_full`, `MS_all_full` are secondary. **TIMEOUT counts as detected** in the primary formula (a mutant that hangs the suite was distinguished from the original); a sensitivity removes TIMEOUT from numerator and denominator. Both variants are always reported; the choice is never made after seeing results. `INVALID` is excluded from every denominator **and its count is always reported** — never silently dropped.

**Differential kill (BDD attribution).** With `S = {m ∈ M : m executed in both modes}` (coverage containment verified and reported):

```
DK_norm        = MS_cov_full(S) − MS_cov_bdd(S)          # primary attribution measure
DK_count       = |K_full(S) \ K_bdd(S)| / |S|
BDD_kill_share = |K_bdd(S)| / |K_full(S)|
```

`DK_norm` answers "what does BDD add beyond the repository's other tests"; `BDD_kill_share` answers "how much of the full suite's oracle is BDD". **`[GATE-DECISION]`** recommend reporting both, headline `DK_norm`, since it is a difference of scores on an identical mutant set.

**7.2 Coverage conditioning (mandatory).** Every oracle-strength value is reported **twice**: over all mutants (`MS_all`) and over mutants covered by the run (`MS_cov`). `mutant_coverage` is a **covariate in every model** (§12.5) and appears in every table. This rule is binding and is reproduced verbatim in the paper:

> A low `MS_all` produced by low `mutant_coverage` says the BDD suite does not execute that code — "not covered" — and is **not** evidence of drift, nor of a weak oracle over the behaviour the suite does exercise. Only `MS_cov` speaks to the discriminating power of the suite over the domain behaviour it covers.

**7.3 Traceability coverage.** An **identifiable business rule** is defined before counting, in priority order. **R1 in-spec identifiers** — a Gherkin `Rule:` block, a tag matching `(?i)@(rule|br|rn|rf|req)[-_ ]?\d+`, or a scenario/feature title containing `\b(BR|RULE|RN|RF|REQ)[-_ ]?\d+\b`; each distinct identifier is one rule. **R2 in-repo requirement documents** — files under `docs/`, `doc/`, `requirements/`, or any `*.md` with a heading matching `(?i)business rules?|requirements?|requisitos|regras de neg[óo]cio`; a rule is a list item or table row beginning with `\b(BR|RULE|RN|RF|REQ|UC)[-_ ]?\d+\b`, or, absent identifiers, a single declarative sentence. The source per repo (`R1`/`R2`/`none`) is recorded in `data/metrics/traceability.csv`. Over repositories with **≥ 3** identifiable rules:

```
rule_trace_coverage = # rules with ≥ 1 scenario referencing the rule id (exact, case-insensitive) / # identifiable rules
```

Only exact identifier matches count as traced; fuzzy title overlap (token Jaccard ≥ 0.6) is computed separately and labelled **exploratory**. Repositories with **no** identifiable rules get `traceability = NOT_APPLICABLE` and are **excluded from this analysis** — never assigned 0, because "unmeasurable" and "zero coverage" are different claims. The N/A count is always reported.

**7.4 The seven drift indicators.** Each is defined so that **higher = more drift-like**, none is sign-flipped after measurement, and each is predicted to associate negatively with `MS_cov_bdd`. Denominators use **active scenarios** `A_r` = all scenarios minus those flagged by D1. **Primary:** D1 `skip_ratio`, D2 `assertion_weakness_ratio`. **Exploratory:** D3 `stale_spec_ratio`, D4 `redundancy_cluster_ratio`, D5 `glue_duplication_ratio`, D6 `literal_bearing_stepdef_ratio`, D7 `mirror_stepdef_ratio`.

**D1 `skip_ratio`.** Tag regex, whole-tag, case-insensitive: `@(skip|skipped|ignore|ignored|wip|pending|todo|manual|notimplemented|not_implemented)\b`. A scenario is skipped if the tag sits on the scenario, its `Examples:` block, or its feature.

```
skip_ratio = |{s ∈ S_r : s is skipped}| / |S_r|      # S_r = all scenarios, static count
```

Parse-only, no execution.

**D2 `assertion_weakness_ratio`.** Coding unit = one step definition `d` (file + line + expression). Classes, applied in order: `STRONG_DIRECT` = an assertion token **and** no W1–W5 match; `STRONG_DELEGATED` = no token but a uniquely name-resolved intra-repo callee at depth ≤ 2 that is `STRONG_DIRECT`; `WEAK` = token present **and** ≥ 1 pattern below; `NONE` = no token, no resolved callee; `UNRESOLVED` = unresolvable target and no token, **excluded from the denominator and counted separately**. Assertion tokens per language live in `pipelines/metrics/assertions/<lang>.py` (Java `assert*`, `assertThat`, `verify(`, `fail(`; JS/TS `expect(`, `.should`, `assert.*`, `t.deepEqual|is|true`; Python `assert`, `pytest.raises`, `self.assert*`).

*Weakening rubric, judgement-coded, reliability measured in §11.* **W1 tautology** — both operands textually identical after whitespace/cast normalisation. **W2 constant truth** — asserted expression is a literal or a literal constructor (`assertTrue(true)`, `expect(1).toBe(1)`, `assert x is not None` on a literal). **W3 unreachable** — assertion in a branch whose condition is a literal, or after an unconditional `return`/`throw` in the same block. **W4 swallowed failure** — enclosing `try` has a `catch`/`except` that neither rethrows nor fails, or the result is assigned and discarded. **W5 self-comparison** — a variable compared to itself, or an assertion on a constant-only expression.

```
assertion_weakness_ratio = (|WEAK|+|NONE|) / (|STRONG_DIRECT|+|STRONG_DELEGATED|+|WEAK|+|NONE|)
```

`UNRESOLVED` may not exceed 25 % of step definitions; above that, D2 for the repo is flagged `low_confidence` and excluded from the confirmatory test.

**D3 `stale_spec_ratio`.** Per active scenario `s`: `t_s` = UTC date of the most recent commit touching its line range at HEAD (`git blame --line-porcelain`, max date from its `Scenario:` line through its last step); `age_s = snapshot − t_s` in days; `n_s` = commits after `t_s` whose paths intersect the domain-layer set (§7.5).

```
stale_spec_ratio = |{s ∈ A_r : age_s ≥ 180 ∧ n_s ≥ 5}| / |A_r|
```

Thresholds (180 d, 5 commits) are **design constants fixed before measurement**; sensitivity at (90 d, 3) and (365 d, 3).

**D4 `redundancy_cluster_ratio`.** Fingerprint each active scenario by the **set of matched step-definition ids** from the §5.3 dry-run JSON (semantic, not lexical); for pairs with non-empty intersection `J_ij = |A_i∩A_j| / |A_i∪A_j|`; edge where `J_ij ≥ 0.8`, a fixed constant.

```
redundancy_cluster_ratio = 1 − (#connected components) / |A_r|
```

Fallback when dry-run JSON is unavailable: normalised step text with parameters replaced (`"…"`→`<STR>`, digits→`<NUM>`, cells→`<CELL>`); `fingerprint_source ∈ {stepdef_id, normalised_text}` recorded per repo.

**D5 `glue_duplication_ratio`.**

```
glue_duplication_ratio = #distinct matched step definitions / #step invocations in A_r
```

1:1 scripted glue gives ≈ 1.0; parameterised, reused specs give ≪ 1.0. From the dry run only.

**D6 `literal_bearing_stepdef_ratio`.** Counted literals per body, by AST where available (JS/TS `@babel/parser`; Python stdlib `ast`) and a documented tokenizer for Java. **Counted**: numeric literals except `0`,`1`,`-1`; string literals of length ≥ 2. **Not counted**: booleans and `null/nil/None`; enum constants; the step expression/annotation literal; assertion *messages*; log/format strings; browser selectors, URLs, XPaths and CSS selectors (fixed regex list) — UI-mechanism constants, not business constants.

```
literal_bearing_stepdef_ratio = #resolved step defs with ≥ 1 counted literal / #resolved step defs
```

Java's tokenizer is regex-based, so J-Java's D6 carries an extra error term, quantified by including D6 in the §11 sample.

**D7 `mirror_stepdef_ratio`.** A **mirror** step re-derives the expected value by repeating the production computation, so the oracle co-varies with the mutant. **M1** the asserted *expected* value is a computed expression (not a literal, `DataTable` or docstring value); **M2** that computation references ≥ 1 value returned by a domain-layer call in the same body; **M3** the asserted *actual* value comes from a domain-layer call in the same body; **M4** the computation reproduces an operation that also exists in domain code (operator and operand shape), established by the rater reading the cited method. Rater label = **mirror** iff `M1 ∧ M3 ∧ (M2 ∨ M4)`, and the rater must cite the domain method inspected. The automated census uses `mirror_loose = M1 ∧ M2 ∧ M3`, computable for every step definition; the rater sample measures its precision and recall, and **precision is reported beside the ratio**.

```
mirror_stepdef_ratio = |mirror_loose| / #resolved step defs
```

**7.5 Domain layer.** **T1 (path)** — matches `(?i)/(domain|domains|model|models|entity|entities|business|core|logic|rules)/` and lies outside the fixed denylist `**/{test*,__tests__,spec,features,migrations,db,ui,web,controllers,node_modules,target,build}/**`. **T2 (framework exclusion)** — removes files importing web, ORM, HTTP-client, UI or serialization frameworks (per-language lists in `pipelines/domain/denylists/<lang>.txt`). **T3 (fallback, only if T1∩T2 is empty)** — non-test files containing ≥ 1 function with a conditional and no I/O call. `domain_tier ∈ {T1+T2, T3, none}` is recorded. `no_domain_layer` is assigned when no tier yields ≥ 1 file, or the dry mutation run yields < 20 mutants. **Validation**: two raters classify 10 repositories' domain sets; per-repo Jaccard, mean and range reported. Systematic disagreement for a language triggers a denylist revision, which — post-gate — is a deviation (§16).

## 8. Mutation protocol

**8.1 Scope.** Mutation applies **only to domain-layer files** (§7.5), in both modes; test code, feature files, step definitions, configuration and generated code are never mutated. Each run records `domain_file_count`, `mutants_generated`, `mutants_in_scope`.

**8.2 Operator classes** — the comparison object is the class, not the tool's identifier string:

| Class | Mutation |
|---|---|
| **S1** | boundary shift `<`↔`<=`, `>`↔`>=` |
| **S2** | predicate negation `==`↔`!=`, `<=`→`>`, `&&`↔`\|\|`, `!x`→`x` |
| **S3** | arithmetic `+`↔`-`, `*`→`/`, `/`→`*`, `%`→`*` |
| **S4** | increment/decrement `++`↔`--`, `+=n`↔`-=n` |
| **S5** | constant replacement: number → `0`/`1`/`-1`, string → `""`, boolean → negation |
| **S6** | return value → `0`/`1`/`true`/`false`/`null`/empty for the declared type |
| **S7** | conditional removal: whole predicate → `true` and → `false` |
| **S8** | switch/branch removal: switch → first arm; one case arm deleted |

Excluded by design (not decision logic): void-method-call removal, member-variable mutation, constructor removal, statement deletion, class-level abstractions, string-append, regex mutation — the mutant must be interpretable as a **proxy** for a business-rule change. `[CITE: mutation operators decision logic domain code]`

**8.3 Per-tool configuration and the availability rule.** The identifiers actually available in each tool are **dumped from the tool's own registry at P1.5** into `data/tooling/mutator-map.csv` (`tool,tool_version,mutator_id,enabled,semantic_class,evidence_path`); the analysis reads that file, so no identifier is hard-coded in prose or code. Configuration intent: **PIT** — mutators and scope by CLI property (`-Dmutators=…`), goal `org.pitest:pitest-maven:mutationCoverage` via `mvnw`, `outputFormats=XML`, **no `pom.xml` edit**. **Stryker** — `mutate` globs restricted to domain files; `testRunner` = `@stryker-mutator/cucumber-runner` (primary) or the built-in `command` runner invoking `cucumber-js` on the same feature paths (fallback); `coverageAnalysis` as the runner requires (`off` for `command`); `reporters` incl. `json`; `thresholds {high:100, low:0}` so no exit code depends on score. **mutmut** — `paths_to_mutate` = domain files; the BDD-only restriction is imposed through `PYTEST_ADDOPTS` selecting only the directories declaring scenarios/steps, verified by the §8.6 collected-test-count assertion.

**Availability rule (pre-registered).** The primary cross-stratum operator set is the **intersection** of classes available in all *surviving* strata; the per-stratum full set is reported as context and every score is labelled with the set used (`full` | `intersection`). If the intersection covers **< 25 %** of generated mutants in any surviving stratum, cross-stratum pooling is abandoned and the paper reports within-stratum results plus a qualitative synthesis. **`[GATE-DECISION]`** Recommend the per-stratum full set as primary, each score being internally valid, with the intersection set as sensitivity only; the intersection maximises comparability while weakening every stratum's oracle measurement.

**8.4 Sampling and budget.** Per repo per mode: if `|M| ≤ 300`, a **census**; otherwise draw **300** mutants with seed `20261125`, stratified proportionally by file with largest-remainder allocation (minimum 1 per non-empty file), random within file. Record `mutants_sampled`, `sampling_fraction`, sampler version. Every score carries a **Wilson 95 % CI** from its tested denominator, so sampling noise is visible in every table. Runtime budget **90 min per repo per mode**; if hit, the run stops, `budget_limited=true` is recorded, the score is computed over mutants that received a verdict, and the achieved count is reported with the widened CI — never presented as a census.

**8.5 Timeouts, no-coverage, equivalents.** *Timeouts* — per-mutant timeout = absolute 30 000 ms plus 3× the baseline BDD-only suite wall-clock where the tool exposes both parameters (PIT `timeoutConstant`/`timeoutFactor`, Stryker `timeoutMS`/`timeoutFactor`); effective values go to the runlog. mutmut's timeout is tool-controlled and recorded verbatim; if it cannot be aligned, that is reported, and is one reason pooled scores are never the headline. *No-coverage mutants* — never dropped: in the `MS_all` denominator, excluded from `MS_cov` by construction, `mutant_coverage` reported for every run. *Equivalent mutants* — no automatic detection is attempted (undecidable in general; no traceable classifier here). Instead (a) `INVALID` counts are reported, (b) the unadjusted survived count is reported with the statement that some survivors are expected to be equivalent, and (c) on a random sample of **40 surviving mutants** across strata, two raters classify "behaviourally equivalent" vs "genuinely undetected" per §11, and that measured proportion yields a **corrected survivor count** as a clearly-labelled secondary estimate with CI. `[CITE: equivalent mutant prevalence estimation]`

**8.6 Mode-integrity assertion (anti-attribution safeguard).** Per repo and mode the harness records the executed-test identifier set and asserts: (1) `executed(bdd) ⊆ executed(full)`, naming map logged; (2) `executed(bdd) ∩ executed(non-BDD tests) = ∅`; (3) `|executed(bdd)| = |scenarios executed in the dry run|`, any retry/skip discrepancy explained in `notes`. Failing (1) or (2) ⇒ `failed_to_measure / tool_incompatibility`: a mis-assigned BDD-only mode would silently corrupt differential kill, the study's central attribution device.

**8.7 Corpus integrity.** The harness may add **at most** one tool configuration file and one report directory to a working copy. No production code, feature file, step definition or test may be modified. Each run records `git diff --stat`; any path outside the declared harness artifacts aborts the run. Repositories needing a source or test edit to build are **not patched** — they are excluded, with the would-be patch described in `reason_detail`.

## 9. Business-rule relevance validation (mutant proxy)

**9.1** Sample: **100** mutants, seed `20261125`, stratified by stratum proportional to measured mutant counts, from included repositories.

**9.2** Two independent raters label each mutant from a standardised packet — the diff, the enclosing method, the file path, and the repo's extracted rules (§7.3) with identifying names stripped. Label ∈ {`relevant`, `plausible`, `not_relevant`, `cannot_judge`}; rubric: `relevant` = breaking this operator/constant would violate a documented or scenario-implicated business rule; `plausible` = touches domain state or a business quantity but no rule is cited; `not_relevant` = infrastructure, logging, formatting, equality/hash plumbing or `toString`. Binary for κ = `relevant` vs rest; `cannot_judge` is reported, never folded.

**9.3 Reporting.** Cohen's κ with bootstrap 95 % CI (§11.3) for relevance, plus base rates. Then for every included repo:

```
MS_cov_bdd(ALL)       # primary outcome — computable for every repo, judgement-free
MS_cov_bdd(RELEVANT)  # secondary — restricted to raters' `relevant` mutants
proxy_gap = MS_cov_bdd(ALL) − MS_cov_bdd(RELEVANT)
```

`MS_cov_bdd(RELEVANT)` is reported per stratum with its Wilson CI, and `proxy_gap` is the quantified proxy cost. If κ < **0.61** `[GATE-DECISION]`, `MS_cov_bdd(RELEVANT)` is demoted to descriptive and the confirmatory outcome remains `MS_cov_bdd(ALL)`.

**9.4 Non-rater criterion evidence.** Injection **I4** (§10.3) supplies it: if a real single-constant business-rule change does not make the BDD suite fail, the suite is demonstrably not a business-rule oracle, whatever its mutation score — the strongest available validity evidence for (or against) the mutant proxy.

## 10. Seeded-drift validation

**10.1 Purpose.** Test whether each static indicator *detects* the drift it should, stays quiet on changes that are not drift, and whether oracle strength moves as predicted — the RQ1 construct-validity evidence.

**10.2 Site and safety.** On **5–8** included repositories whose BDD-only suite passes at HEAD, in a **separate clone** at `work/injections/<repo_id>/` on branch `drift-injection/<repo_id>`. The measured corpus at `work/repos/<repo_id>/` is never touched and its HEAD SHA is re-verified after the campaign. Nothing is pushed upstream.

**10.3 Injection types** — six per repository (4 target + 2 control) ⇒ 30–48 observations, each a single scripted minimal edit, with the patch and its SHA-256 stored.

| ID | Injection | Target | Indicator must | Predicted Δ`MS_cov_bdd` |
|---|---|---|---|---|
| **I1** | add `@skip` to a scenario that currently kills ≥ 1 mutant | D1 | **flag** | decrease (if the scenario killed nothing, predicted unchanged; its kill set is recorded beforehand) |
| **I2** | delete or loosen the assertion of a step definition used by ≥ 1 scenario | D2 | **flag** | decrease |
| **I3** | rewrite a step definition into a mirror recomputing the expected value from production internals | D7 | **flag** | decrease |
| **I4** | change one business constant in domain code (threshold/limit/percentage) visibly | none (code drift) | — | **suite must FAIL** |
| **C1** | comment/format-only edit in a feature file and a step definition | all seven | **stay silent** | 0 (± tolerance) |
| **C2** | add a scenario with a real strong assertion for an already-covered rule | all seven | **stay silent** | ≥ 0 |

**I4 is the business-rule perturbation probe.** Detection = the BDD-only suite transitions pass → fail. A non-detection means the suite did not notice a real business-rule change, the most persuasive single-repo evidence that it is not a business-rule oracle. I4's outcome is binary per repo, reported with an exact CI, never averaged into a mutation score.

**10.4 Outcomes.** `sensitivity(d) = # injections of d's target type flagged by d / # such injections`; `specificity(d) = # control injections not flagged by d / # controls`. Both with **Clopper–Pearson exact 95 % CIs**, per indicator and pooled across repositories — pooling is legitimate here because the unit is the *injection*, an independent edit; this is the one place where the unit is deliberately not the repository, and the paper must say so. "Moves as expected" for Δ`MS_cov_bdd` = sign matches §10.3 **and** `|Δ|` exceeds the §15.4 instability tolerance; otherwise the injection is scored `inconclusive` and reported, not discarded. RQ1's rule (§1.4c) uses sensitivity ≥ 0.80 and specificity ≥ 0.90 per primary indicator.

## 11. Inter-rater reliability

**11.1 Sample.** **120** step definitions, seed `20261125`, stratified by stratum and by automated class (`STRONG`/`WEAK`/`NONE`) so rare classes are not swamped. Two properties coded independently: **`assertion weakened`** (D2's W1–W5 vs strong) and **`mirror step`** (D7's M1–M4). D6's literal coding and §8.5's survivor-equivalence sample use their own samples under the same procedure.

**11.2 Packet and blinding.** Each item shows the step-definition body, the calling step text(s), the file path with repository name replaced by a code, and (for D7) up to two candidate domain methods retrieved by name — no scores, no repo identity, no automated label. Raters code in separate files, are not shown each other's labels, and disagreements are adjudicated in a third pass with the rubric; **raw and adjudicated labels are both retained**. Any LLM assistance is disclosed per venue rule V16 and the statistic labelled "human–LLM agreement", never inter-rater reliability.

**11.3 Statistic.** Cohen's κ = `(p_o − p_e)/(1 − p_e)` per property, with a **bootstrap percentile 95 % CI** (2 000 item resamples, seed `20261125`), plus PABAK `2p_o − 1` when either class's prevalence exceeds 0.85 or falls below 0.15 — κ is deflated by extreme prevalence, so both numbers are reported. Interpretation bands are quoted from a verified source: `[CITE: Landis Koch 1977 kappa benchmark bands]`. A judgement-coded indicator with κ < 0.61 is reported as **not reliably measured** and excluded from the confirmatory family (demoted to descriptive), with the failure published.

**11.4 Fallback without a second human rater.** The same rater codes the identical packet at two time points **≥ 7 days apart**, blind to the first pass; the statistic is then **intra**-rater κ with the same CI machinery, labelled `intra-rater`. The paper **must** state which design was used, in the method section and in the abstract's limitation sentence. The fallback is weaker evidence and is never described as inter-rater reliability.

## 12. Statistics (declared before measurement)

**12.1 Unit and n.** Unit = repository, one row each; design target `n = 30` included, cap 40 (§2.7). No analysis treats mutants, scenarios or steps as independent observations except §10.4 (injections) and §11 (items), each of which says so. Every estimate carries a CI; a null association is reported with its CI and an explicit statement of what it rules out under §12.6. Nothing is called "a trend" without a CI excluding the null, and no p-value appears without an effect size.

**12.2 Confirmatory family — exactly two primary indicators.** `D1 skip_ratio` and `D2 assertion_weakness_ratio`, each against the single primary outcome `MS_cov_bdd`, **adjusted for `mutant_coverage`**. Two tests, Holm-corrected across the two (effective α for the smaller p is 0.025). **Everything else is exploratory**: D3–D7 form one exploratory family of 5 tests against `MS_cov_bdd`, Holm-corrected within that family and labelled exploratory in every table. Remaining comparisons (secondary outcomes, traceability, longitudinal joins) are descriptive — point estimates with CIs, p-values only if marked "unadjusted, exploratory".

**12.3 Headline rule (binding).** **A single pooled Spearman correlation is never the headline.** Reporting order is fixed: (i) per-stratum Spearman ρ with bootstrap 95 % CIs (2 000 resamples, seed `20261125`); (ii) the pooled estimate with its CI; (iii) an explicit statement that PIT/Stryker/mutmut scores are not on a common axis, so the pooled figure averages within-stratum associations rather than correlating a homogeneous scale. Strata use their own operator set (§8.3); the intersection-set sensitivity is reported alongside.

**12.4 Models.** **Per stratum** (`n_s ≥ 8`, else descriptives only and the stratum is declared underpowered): `g(MS_cov_bdd) ~ β0 + β1·indicator + β2·mutant_coverage + β3·log1p(stars) + β4·scenario_count`, `g` = identity (primary) or logit (sensitivity). ρ is the reported effect size; β1 the adjusted effect with bootstrap CI. **Pooled**: (a) fixed-effects model with `stratum` as a **fixed** factor (three levels cannot support a stable random effect), `indicator`, `mutant_coverage`, and a tested `stratum × indicator` interaction, reported whatever its result; (b) **cluster bootstrap by stratum** (resample repositories within stratum, 2 000 reps, seed `20261125`) as the **primary pooled CI**, because cluster-robust SEs with three clusters are unreliable; (c) a mixed model with random intercept for stratum only as a sensitivity, with a warning if it fails to converge.

**12.5 Covariates.** `mutant_coverage` is mandatory in every model — never omitted, never replaced by line coverage. `log1p(stars)`, `scenario_count`, repo age and domain LOC are pre-specified adjustment candidates; every model is reported with and without them, so no result depends on an unstated adjustment set.

**12.6 Power and the smallest detectable effect.** On the Fisher-z scale appropriate to Spearman's ρ:

```
SE(z) = 1.030 / sqrt(n − 3)          z = atanh(ρ)
|ρ|_min:  atanh(ρ) = (z_{1−α/2} + z_{1−β}) · SE(z)
```

Evaluated at the **declared design n** (two-sided α = 0.05, power 0.80):

| n | 10 | 20 | 30 | 40 |
|---|---|---|---|---|
| min detectable \|ρ\| | 0.80 | 0.60 | **0.50** | 0.44 |

At the design target `n = 30` only **|ρ| ≳ 0.50** is detectable; with Holm-adjusted α = 0.025 the floor rises to |ρ| ≈ 0.54, and at `n_s = 10` it is |ρ| ≈ 0.80, so per-stratum tests are essentially descriptive unless the association is very strong. **These limits must be stated in the paper**: the study can detect strong associations and is uninformative about weak or moderate ones. At P4 the table is recomputed at the achieved and per-stratum n `[P3-DERIVED]`; those values replace it in the manuscript, the formula above being the pre-registered procedure.

**12.7 Distributional handling.** `MS_cov_bdd` is bounded and often near 1 in small well-tested repos (ceiling effect), and undefined when the tested denominator < 10 — such repos are reported as `insufficient_tested_mutants` and excluded from models, with the count disclosed. Primary scale = identity on [0,1], sensitivity = logit; proportion indicators on their natural scale, logit in sensitivity. A zero-variance indicator is reported descriptively with an explicit note, not fitted.

## 13. Longitudinal component (RQ3)

**13.1 Static history mining (no builds).** Per repo, on the default branch:

```
git log --reverse --date=short --format=%H|%cI -- <feature, step-def, domain paths>
```

Recompute at **K = 12** commits chosen deterministically: sort commits touching those paths by index and take `round(i·(N−1)/11)`, `i = 0..11`, duplicates removed — so the sample spans the lifetime and is reproducible from the log. At each commit materialise blobs with `git show <sha>:<path>` and compute D1, D2, D5, D6, D3's `n_s` inputs, and the counts `feature_file_count`, `scenario_count`, `stepdef_count`. D4 and D7 are computed at the 12 points only where cheap, else at HEAD and the 12-month snapshot only.

**13.2 Static erosion statistic.** Repo-level **Theil–Sen slope** of `skip_ratio` and of `assertion_weakness_ratio` against commit time (days since first commit). Report median slope, IQR, and the proportion of repositories with a positive slope with an **exact binomial 95 % CI** — the primary longitudinal statistic, being distribution-free and tolerant of 12-point series. A mixed model with random intercept and slope is fitted only as a sensitivity, and only if ≥ 20 repositories have complete 12-point series; otherwise it is not attempted and the omission is stated.

**13.3 Two-snapshot mutation.** For the subset building at both commits: HEAD and the **pinned 12-month ancestor** = last commit on the default branch with committer date ≤ `HEAD_date − 365 days` (if none, the repo is omitted and the fact reported). Both SHAs recorded. Because mutant sets differ across commits:

```
ΔM_all    = MS_cov_bdd(HEAD) − MS_cov_bdd(T12)                        # all mutants
S_common  = mutants matched by (file, operator class, original-line content hash) present at both commits
ΔM_common = MS_cov_bdd(HEAD, S_common) − MS_cov_bdd(T12, S_common)     # primary change estimate
```

`ΔM_common` is reported only if `S_common` covers **≥ 50 %** of HEAD mutants; otherwise the repo's change estimate is flagged `low_overlap` and reported descriptively. `ΔM_common` measures **change between two snapshots** and the paper calls it exactly that — not a trend, not a rate.

**13.4 Join.** Association between HEAD indicators (D1–D7) and `ΔM_common` is **exploratory** (small n: only repos building at both SHAs), reported as ρ with bootstrap CI per stratum. Oracle erosion (negative Δ) is reported with magnitude and CI, and the number of repositories improving is given equal prominence.

## 14. Threats to validity

| # | Threat → mechanism, plausible bias | Quantification | Residual |
|---|---|---|---|
| **T1** | Survivorship / build attrition; buildable repos may have simpler dependency graphs, hence simpler domains → plausibly *upward* on strength | Full funnel by category (§5.5); included-vs-excluded on 6 covariates (§6.2); worst-case percentile bounds and multiple-imputation sensitivity (§6.3) | May correlate with an unmeasured construct ("engineering care") that also drives strength; bounds, not correction |
| **T2** | Mutants are not business rules; generic operators ≠ business-rule changes → unknown | Two-rater relevance κ and `proxy_gap` (§9.3); I4 perturbation probe as criterion evidence (§10.3) | If κ < 0.61 the proxy claim weakens and is demoted to descriptive |
| **T3** | Attrition correlated with suite quality; sophisticated suites need services/DB/browsers and fail here (no Docker) → *downward*: the strongest suites are likeliest to be unmeasurable | `failed_to_build` rate by stratum and by stars/scenario count; the `service_dependency`/`browser_required`/`database_required` share as the mechanism's footprint | Cannot be repaired without isolated builds; the study's largest single limitation |
| **T4** | Multi-language toolchain differences (operators, timeout semantics, coverage granularity) → unknown | Within-stratum-first analysis (§12.3); operator-class table (§8.2) with availability dumped empirically (§8.3); intersection-set sensitivity | Cross-stratum score differences are never read as suite-quality differences, a prohibited inference |
| **T5** | Coverage confounding; a low score may be low coverage, not weak discrimination → *downward* on `MS_all` | `MS_cov` always beside `MS_all`; `mutant_coverage` mandatory covariate; §7.2 rule quoted verbatim | Coverage may itself be endogenous (a drifting suite stops covering new code), so its association with the indicators is reported, not silently partialled out |
| **T6** | BDD attribution; a strong suite may be strong for non-BDD reasons → *upward* on any naive "BDD is strong" reading | `DK_norm`, `DK_count`, `BDD_kill_share` on an identical mutant set (§7.1); mode-integrity assertion (§8.6) | Repos failing `executed(bdd) ⊆ executed(full)` are dropped, not patched |
| **T7** | Drift measured on only two mutation snapshots; two points cannot separate trend from fluctuation or from one refactor → unknown | 12-point *static* series (§13.1); mutation change reported as a single interval Δ with CI | No mutation trend is claimed anywhere; "erosion" is used only for indicators over ≥ 12 points and only with the sign-test CI |
| **T8** | Rater subjectivity (W1–W5, D7's M4, relevance, equivalence) → unknown | κ with CI + PABAK (§11.3); adjudication retained; primary indicators chosen to be syntactic; automated components validated against the rubric (precision/recall of `mirror_loose`) | The single-coder fallback is weaker and is labelled as such (§11.4) |
| **T9** | Public repos ≠ industrial practice; public Cucumber suites over-represent demos, course projects and OSS products → likely *favourable* to corpus sophistication | Frame restriction as a scope condition; the sampled distribution of stars/age/size/scenario count describes what was actually sampled | Claim scoped to "public Cucumber-style suites in the defined frame", never to "industry practice" |
| **T10** | **No build isolation (no Docker): cross-repo contamination.** Shared caches, `PATH`, JDK 22 only, `JAVA_HOME` unset, no Maven/Gradle; one repo's package or env var can change another's result → plausibly noise rather than bias | Per-repo cache localisation (`-Dmaven.repo.local=work/m2/<repo_id>`, per-repo `node_modules`/venv, workspace-local npm+pip caches); per-run environment manifest (§15.2); **repeatability probe** on a random 20 % subsample from a fresh clone later, reporting `instrument_instability`; any repo differing by > 0.05 absolute is re-run and both values reported | Third-party reproduction of a given build is not guaranteed: everything needed is recorded (§15), but the host is not hermetic |
| **T11** | Timeout / instrument artefacts; slow host, no isolation ⇒ false timeouts, and counting timeouts as kills inflates scores → *upward* | Timeout counts per run; both formula variants (§8.5); T10's tolerance gates "moves as expected" (§10.4) | A slow-mutant timeout cannot be distinguished from a true non-terminating mutant |

## 15. Reproducibility plan

**15.1 Per-run record.** Every harness invocation appends **one** JSON object to `results/runlog.jsonl` (append-only, never rewritten): `run_id, utc_start, utc_end, phase, repo_id, git_head_sha, working_tree_sha256, dirty_paths, mode (bdd|full|dry|inject|none), command, argv_sha256, exit_code, timeout_hit, tool_name, tool_version, tool_config_sha256, mutator_set_id, java_version, node_version, npm_version, python_version, bdd_tool_version, os_version, hostname, utc_offset, seed, mutants_generated, mutants_sampled, sampling_fraction, mutants_killed, mutants_survived, mutants_timeout, mutants_nocoverage, mutants_invalid, mutant_coverage, ms_all, ms_cov, budget_limited, mode_integrity_ok, artifacts[{path,sha256,bytes}], log_path, notes`. `working_tree_sha256` hashes the sorted `git status --porcelain` output, so "the corpus was not modified" is verifiable rather than asserted; `tool_config_sha256` hashes the effective configuration actually used.

**15.2 Environment manifest.** One `results/env/<run_id>.json` per run: full `PATH`, cache redirections (`npm_config_cache`, `PYTHONUSERBASE`, `-Dmaven.repo.local`), `JAVA_HOME` (unset), resolved `java`/`node`/`python` executables, and a pre-run listing of every cache the run will write to — what makes T10 auditable after the fact.

**15.3 `results/RUNLOG.md`.** Generated by `scripts/render_runlog.py` from `runlog.jsonl`, never hand-edited: one markdown row per run with short run id, UTC, repo, phase, mode, command (truncated), exit, mutants (generated/sampled), killed/survived/nocov/timeout/invalid, `MS_all`, `MS_cov`, coverage, flags (`budget_limited`, `mode_integrity_ok`, `timeout_hit`) and log link. Re-rendering an unchanged `runlog.jsonl` must yield a byte-identical `RUNLOG.md`; the harness self-test asserts it.

**15.4 Instrument-stability probe.** 20 % of included repositories (seed `20261125`) are re-measured from a **fresh clone** later; `instrument_instability = |MS_cov_bdd(run2) − MS_cov_bdd(run1)|`. Its distribution (median, 95th percentile) is reported and its 95th percentile defines the §10.4 tolerance — the empirical measurement of the no-Docker threat.

**15.5 Retention.** Per repo: pinned HEAD and T12 SHAs, exact commands, tool reports (XML/JSON), domain-layer file list, indicator inputs, logs. Licences are recorded (E2); no repository content is redistributed beyond diff-level quotation permitted by its licence, only derived measurements being published in full. Per V23 the deposit is the harness, frame, attrition log, metric tables and runlog; repositories are cited by URL and pinned SHA.

## 16. Deviations policy

**16.1 Freeze.** At the P1 gate `docs/method.md` is frozen: its SHA-256 goes to `results/RUNLOG.md` (`prereg-freeze`) and to the OSF deposit (V21 permits pre-registration). Collection may not begin under any other version.

**16.2 Any post-gate change is a deviation.** A change to sampling, eligibility, strata, indicators, formulas, thresholds, operator sets, model specification, the confirmatory family or the power procedure is recorded in `docs/DEVIATIONS.md` with exactly these columns:

```
id,utc_timestamp,phase,pre_registered_text_sha256,what_changed,why,trigger_evidence,affected_artifacts,approved_by,disclosed_in_paper_section
```

`trigger_evidence` must point to a concrete artefact (pilot log, tool failure, measured impossibility); an unexplained deviation is a protocol violation. Approvals are recorded by role, never by name, during double-anonymous review.

**16.3 Consequences for the paper.** Every deviation is disclosed in the method or limitations section in the same wording as the log's `what_changed`. If it touches a **pre-specified primary** analysis (D1, D2, `MS_cov_bdd`, the Holm family, or the power procedure), the paper reports **both** the pre-registered and the deviated analysis, with the pre-registered one leading. Nothing is quietly replaced.

**16.4 Pilot- and measurement-derived values are not deviations.** `[PILOT-DERIVED]` values (sampling multiplier, runtime caps, timeout parameters, tool mutator identifiers, power inputs) are *expected* to be fixed after P1.5 and before the gate, and are recorded in the gate report. `[P3-DERIVED]` values (achieved n, per-stratum n, achieved mutant counts) are measurements, not decisions.

## Appendix A — `[GATE-DECISION]` items

| # | Decision | Recommendation |
|---|---|---|
| A1 | §2.6 seed `20261125` | adopt |
| A2 | §2.7 target n = 30, cap 40 | adopt; raise only if pilot yield and runtime permit |
| A3 | §4.4 Python stratum: at risk vs dropped | at risk, reported additively |
| A4 | §7.1 RQ2 headline: `DK_norm` vs `BDD_kill_share` | `DK_norm` headline, both reported |
| A5 | §8.3 primary operator set: per-stratum full vs intersection | per-stratum full primary, intersection as sensitivity |
| A6 | §9.3 relevance κ threshold 0.61 | adopt |
| A7 | §12.2 primary family = exactly 2 tests | adopt |
| A8 | §11.4 single-rater fallback (intra-rater κ) acceptable | adopt, with mandatory disclosure |
| A9 | Is "public Cucumber-style suites in a defined frame" an acceptable IS-scope claim (V2–V5)? | needs positioning work in the paper; not a method change |
