# PROTOCOL.md — Assessing the Oracle Strength of a Cucumber-Style Suite

**What this is.** A step-by-step protocol an organisation can apply to its *own* BDD suite to answer
two questions: *is this specification layer still able to detect a change in the business rules it
claims to describe?* and *is that ability decaying?* It is the practical artefact of the associated
study and is written to be executed by a team, not by a researcher.

**What this is not.** It is not a quality certificate, and a low score here is not, by itself,
evidence of a defect. Read §7 before drawing any conclusion. The protocol measures one property —
the discriminating power of the specification layer over the domain behaviour it executes — and
nothing else.

**Design-science grounding.** The protocol is an artefact (method) designed to address an
organisational problem: the business rule lives in three places that drift apart — the requirement,
the Gherkin scenario, and the code — and the drift is invisible to coverage metrics. It is evaluated
in §8.

---

## 1. Why coverage is not enough

Coverage tells you that a line ran. It cannot tell you that anything checked the result. A suite can
reach 97 % statement coverage and still fail to distinguish a deliberately altered business rule:
the original authors of mutation testing observed mean mutation scores of 0.78 at 97.2 % statement
coverage in an industrial Ruby project (Li et al., 2015), and a later study of 45 Maven projects
found the correlation between coverage and mutation score falls from 0.75 to 0.21 once you condition
on covered code (Jain et al., 2023). Coverage is a *reach* measure. Mutation score is a
*discrimination* measure.

This protocol therefore measures discrimination, and always reports reach beside it, so that the two
are never confused.

---

## 2. Preconditions

Do not start unless all of these hold. If one does not, fix it first; the protocol cannot compensate.

| # | Precondition | Why |
|---|---|---|
| P1 | The BDD suite runs **green** at the commit you intend to measure | A red baseline makes every mutant look "killed", inflating the score to a meaningless 100 % |
| P2 | You can run the BDD suite **alone**, without the rest of the test suite | Needed to attribute detection to the specification layer (§4) |
| P3 | There is an identifiable **domain layer** (§3) | Mutating glue, UI or infrastructure measures something else |
| P4 | Mutation tooling is pinned to an exact version and recorded | Tools are not interchangeable: the same subjects yielded equivalent-mutant counts of 203 / 94 / 382 / 43 across four Java tools, and no tool subsumed the others (Kintis et al., 2018) |

---

## 3. Step 1 — Delimit the domain layer

Mutate the code where business decisions live, not the code that moves data.

**Tier 1 (path).** Files under a path segment matching
`/(domain|domains|model|models|entity|entities|business|core|logic|rules)/`, excluding
`test*, __tests__, spec, features, migrations, db, ui, web, controllers, node_modules, target, build`.

**Tier 2 (framework exclusion).** From Tier 1, remove files whose imports name a web framework, an
ORM, an HTTP client, a UI toolkit or a serialisation library. Keep the list per language under
version control.

**Tier 3 (fallback, only if Tiers 1–2 are empty).** Non-test files containing at least one function
with a conditional and no I/O call.

Record which tier you used. If none yields at least one file — or the dry mutation run yields fewer
than 20 mutants — record `no_domain_layer` and stop: your suite has no measurable specification
layer, which is itself an answer.

**Sanity check.** Two people independently delimit the domain layer for 10 repositories and compare.
Report the Jaccard agreement per repository. If they disagree systematically for a language, your
tier-2 lists are wrong.

---

## 4. Step 2 — Measure oracle strength, twice

Run mutation analysis in two modes over the **same mutant set**:

- **BDD-only**: the BDD runner alone.
- **Full**: everything the project runs in CI.

Then, for repository *r*, with mutants `M`, and `Cov` the mutants the run executed:

```
MS_all(mode)    = (KILLED + TIMEOUT) / (KILLED + SURVIVED + TIMEOUT + NO_COVERAGE)
MS_cov(mode)    = (KILLED + TIMEOUT) / (KILLED + SURVIVED + TIMEOUT)
mutant_coverage = (KILLED + SURVIVED + TIMEOUT) / (KILLED + SURVIVED + TIMEOUT + NO_COVERAGE)
```

**Report both `MS_all` and `MS_cov`, always, side by side.** This is the single most important rule
in the protocol:

> A low `MS_all` produced by low `mutant_coverage` says the BDD suite does not execute that code —
> "not covered" — and is **not** evidence of drift or of a weak oracle over the behaviour the suite
> does exercise. Only `MS_cov` speaks to the discriminating power of the suite over the domain
> behaviour it covers.

**Attribute detection to the specification layer.** Let `S` be the mutants executed in *both* modes
(containment — everything the BDD suite runs, the full suite also runs — is an invariant you should
assert, not assume):

```
DK_norm        = MS_cov(full, S) − MS_cov(bdd, S)     # what the rest of the suite adds
BDD_kill_share = |K_bdd(S)| / |K_full(S)|             # how much of the oracle is the BDD layer
```

`DK_norm` is the honest answer to "how much does our BDD layer actually buy us". A high absolute
score with a near-zero `DK_norm` means the suite is strong for reasons *unrelated* to the Gherkin.

**Mutant protocol.** Restrict operators to decision logic: conditionals boundary, negated
conditionals, arithmetic, constants, return values. State the exact operator set per tool. Sample
mutants with a fixed seed under a per-repository budget if the run is too slow. Handle timeouts
(count as detected; also report the sensitivity that excludes them), no-coverage mutants (report the
count; never let them dilute `MS_cov`), and equivalent mutants (report the count; never silently
drop them).

---

## 5. Step 3 — Measure seven drift indicators

Each is defined so that **higher = more drift-like**, and none may be sign-flipped after you see the
results. Denominators use **active** scenarios — all scenarios minus those the skip tags already
flag.

| ID | Indicator | Definition | Status |
|---|---|---|---|
| **D1** | `skip_ratio` | Scenarios carrying `@skip/@ignore/@wip/@pending/@todo/@manual` (on the scenario, its `Examples:` block, or its feature) ÷ all scenarios | **Primary** |
| **D2** | `assertion_weakness_ratio` | Step definitions that are `WEAK` or `NONE` ÷ all resolved step definitions (see below) | **Primary** |
| **D3** | `stale_spec_ratio` | Active scenarios whose last-touching commit is ≥180 days old **and** with ≥5 domain commits since ÷ active scenarios | exploratory |
| **D4** | `redundancy_cluster_ratio` | 1 − (connected components of the scenario-overlap graph at Jaccard ≥0.8) ÷ active scenarios | exploratory |
| **D5** | `glue_duplication_ratio` | Distinct matched step definitions ÷ step invocations in active scenarios | exploratory |
| **D6** | `literal_bearing_stepdef_ratio` | Resolved step definitions containing ≥1 counted literal ÷ resolved step definitions | exploratory |
| **D7** | `mirror_stepdef_ratio` | Step definitions that re-derive the expected value by repeating the production computation ÷ resolved step definitions | exploratory |

**Classifying a step definition for D2.** A step is `STRONG_DIRECT` if it carries an assertion and
matches no weakening pattern; `STRONG_DELEGATED` if it calls an intra-repository method (depth ≤2)
that is `STRONG_DIRECT`; `WEAK` if it has an assertion **and** matches a weakening pattern;
`NONE` if it has neither. Weakening patterns:

- **W1 tautology** — both operands textually identical after normalisation.
- **W2 constant truth** — `assertTrue(true)`, `expect(1).toBe(1)`, `assert x is not None` on a literal.
- **W3 unreachable** — assertion in a branch whose condition is a literal, or after an unconditional
  `return`/`throw`.
- **W4 swallowed failure** — the enclosing `try` has a `catch` that neither rethrows nor fails.
- **W5 self-comparison** — a variable compared to itself, or an assertion on a constant-only
  expression.

```
assertion_weakness_ratio = (WEAK + NONE) / (STRONG_DIRECT + STRONG_DELEGATED + WEAK + NONE)
```

If more than 25 % of step definitions are unresolvable, mark D2 `low_confidence` and do not use it
in a confirmatory test.

**D6 literal exclusions.** Do not count booleans, `null`, enum constants, assertion *messages*, log
or format strings, or UI-mechanism constants (selectors, URLs, XPaths). Those are not business
constants, and counting them turns a business-rule signal into a measurement of how verbose your
page objects are.

**D7, honestly.** D7 is the least reliable indicator: it needs a human judgement about whether a
computation "reproduces" domain logic. Automate only the loose form (expected value is computed,
it references a domain call, and the actual comes from a domain call) and report human-measured
precision beside it. If you cannot resource a rater, report D7 as `census-only, unvalidated`.

---

## 6. Step 4 — Look for accumulation over time

Static history mining needs no old builds. Pick **K = 12** commits touching the features, step
definitions or domain layer, at even index positions across the lifetime (deterministic, so it is
reproducible), and recompute D1, D2, D4, D5, D6 at each.

Compute the **Theil–Sen slope** of each indicator against time — distribution-free and robust for
short series. Report the median slope, the interquartile range, and the proportion of repositories
with a positive slope with an exact binomial confidence interval.

If you also want the score to move, measure mutation at HEAD and at one pinned ancestor
(~12 months back). Match mutants across the two commits by *(file, operator class, original-line
content hash)* and report the change only on the **common** set:

```
ΔM_common = MS_cov_bdd(HEAD, S_common) − MS_cov_bdd(T12, S_common)
```

If `S_common` covers less than half of the HEAD mutants, do not report a change estimate — report
`low_overlap`. And call it what it is: **a change between two snapshots, not a trend and not a rate.**

---

## 7. Step 5 — Interpret, and refuse to over-interpret

1. **"Not covered" ≠ "drifted".** Check `mutant_coverage` first. A suite that does not execute the
   domain code has a coverage problem, not an oracle problem.
2. **A snapshot is not a trend.** A single low score at HEAD says nothing about decay. Only the
   longitudinal series speaks to accumulation.
3. **Association is not causation.** Static indicators co-vary with weak oracles; the protocol does
   not establish that removing an `@wip` raises your mutation score.
4. **Report the detectable-effect floor.** With *n* repositories, Spearman associations below
   roughly `tanh((1.96+0.84)·1.03/√(n−3))` are not detectable — at n = 30 that floor is |ρ| ≈ 0.50.
   An association under the floor is *not measured*, which is not the same as *absent*.
5. **Never pool across tools.** PIT, Stryker and mutmut scores are not on a common axis. Analyse
   within a language/tool stratum; if you must summarise, say that you are averaging
   within-stratum associations.
6. **Disclose what you could not measure.** Attrition is a finding, not an embarrassment. Report how
   many candidate repositories you had to exclude, by category, and compare included against
   excluded on size, age and activity — that is how a reader judges survivorship bias.

---

## 8. Evaluation of this protocol

**Read this before relying on any indicator.** The protocol's own claims are bounded by how much of it
has actually been evaluated, and the associated study did **not** complete the full evaluation. Stated
plainly, so that a practitioner is not misled:

| Element | State |
|---|---|
| Tool feasibility (Java, JS/TS) | **Demonstrated.** Both paths were driven end to end with per-mutant coverage and per-scenario attribution. |
| Static indicators D1–D7 | **Implemented and runnable**; D2 and D7 are heuristic approximations of the judgement-coded rubric (see §5). |
| Longitudinal indicators over history | **Implemented; not exercised on real data** in the associated study (the materialised repositories carried no VCS history). |
| **Seeded-drift validation** | **NOT PERFORMED.** The injection experiment in §10 of the study protocol was not carried out. The indicators are therefore **not empirically validated against known ground truth**, and no detection rate exists. |
| Inter-rater reliability | **NOT PERFORMED.** No independent human raters were available. No kappa is reported for any indicator, and D7's precision is unknown. |
| Oracle strength on a public corpus | **Not established.** The associated study found no public repository that both built and produced a green Gherkin baseline within its budget, so no corpus-level score is reported. |

Two consequences for anyone applying this protocol. First, treat D2 and D7 as **screening heuristics**
that flag candidates for human inspection, not as measurements with known accuracy. Second, your own
application of the protocol is the first real validation of it; we would be glad to know the result.
Where the study could not complete an element, that is stated in the paper's limitations. **A protocol
that reports its own gaps is more useful than one that hides them**, and practitioners should apply the
same standard to their own results.

---

## 9. Minimum reporting checklist

Before you present a number to management, confirm you can answer all of these:

- [ ] Mutation tool and exact version; operator set; mutant budget; sampling seed.
- [ ] Baseline was green; if not, what was excluded and why.
- [ ] Domain-layer tier used, and how the domain set was delimited.
- [ ] `MS_all` **and** `MS_cov` **and** `mutant_coverage`, reported together.
- [ ] `DK_norm` and `BDD_kill_share` if the full suite was also measured.
- [ ] Counts of equivalent, no-coverage and invalid mutants.
- [ ] How many candidate repositories were excluded, by category.
- [ ] n, and the minimum detectable association at that n.
- [ ] For any longitudinal claim: the number of snapshots, and that a change is not a trend.
