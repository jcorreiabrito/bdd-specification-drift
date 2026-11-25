# RED-TEAM REVIEW — `paper/main.tex` + `paper/sections/*`

**Reviewer:** S5. **Venue:** iSys (Qualis A4). **State:** tree at 2026-11-25 ~10:30 (UTC−03);
`numbers.tex` regenerated 10:25:18, `bs_java.csv` written 10:27:32, so figures were still moving (§8.4).
18 pages confirmed in `paper/main.log`. **Verdict: not submittable** — three S0 defects.

---

## 1. Fatal issues

### F1. The "pre-registered" claim is unevidenced, and the executed protocol is a different protocol.

`05-method.tex:4–5`: *"The method was pre-registered in a versioned protocol document before any corpus
measurement, and the commit timestamp is its evidence."* Falsified three ways.

1. `docs/method.md:5` and §16.1 make the freeze artefact *"SHA-256 of this file → runlog entry
   `prereg-freeze` in `results/RUNLOG.md`"*. `RUNLOG.md` has **zero** occurrences of `prereg` or `freeze`
   and five hand-written entries (R001–R005).
2. `docs/DEVIATIONS.md:8`: *"the P1 gate has NOT closed. No corpus has been measured"*; §C: *"None yet — the
   gate has not closed."* An unfrozen draft is not a pre-registration, and `05-method.tex:59`'s *"before the
   gate closed"* is true only because the gate never closed.
3. Executed ≠ pre-registered. Registered but absent: stop at 40 included rather than census the frame
   (§2.7); E6 active-or-notable; E7 tooling allowlist + description regex; E8 "≥20 mutants in a dry run";
   the intra-rater κ fallback (§11.4); the seeded-drift campaign (§10); percentile bounds and imputation
   (§6.3); `rule_trace_coverage` (§7.3); the 40-survivor equivalent-mutant sample (§8.5). Implemented but
   never registered: the 12-slug × 5-filter × 6-page grid (`05-method.tex:20–26` vs §2.3's 10 × 4 × 2 ×
   10); "≥10 non-test sources" replacing E8 (`05-method.tex:43–55`); the `fetch_failed_413` and
   `no_tests_found` categories (absent from §5.2).

`05-method.tex:57–60` then claims criteria 7–8 *"were added after the pilot"* because a *"naive rule —
features, steps, build, licence"* admitted tooling. That naive rule is **not** in the pre-registration,
which already had a tooling exclusion (E7) and a domain-layer criterion (E8). The paper misdescribes its own
protocol to make an unlogged change look like a disclosed refinement — which `docs/method.md` §3.2 forbids:
*"no criterion may be added, relaxed, reinterpreted or applied selectively."*

**Fix:** produce a dated freeze commit plus `prereg-freeze` entry and rewrite §Method as as-executed with a
pre-registered-vs-executed table, or delete every use of "pre-registered" (including the abstract's
`[Method]`) and reframe as exploratory. Keep the claim and the package's own `DEVIATIONS.md` refutes it.

### F2. There are no units of analysis, and the pre-registered drop rule voids the confirmatory analysis.

`numbers.tex:23–31`: `\Ngreen{0}`, `\Nmeasured{0}`, `\Nhistory{0}`, `\Nwithfull{0}`. RQ2 and RQ3 have zero
observations; RQ1 rests on two hand-written suites totalling 62 mutants.

`docs/method.md` §4.3 DR1 drops a stratum with *"< 8 repositories measurable end-to-end"*. With 0 measured,
**both strata must be dropped and the confirmatory family is void by the paper's own rule**. The paper never
invokes DR1. Instead `06-results.tex:166–167` says *"the pre-registered detectable-effect floor at the
achieved $n$ is $|\rho|_{\min} = \FloorRho$"* — rendering as *"not defined (no measured units)"*
(`numbers.tex:7`) — and the next sentence compares an association against it. `09-conclusion.tex:26–29`
asserts *"the detectable-effect floor … is well above any effect the design could plausibly have detected."*
There is no floor; at $n=0$ the formula in `05-method.tex:215` ($1.030/\sqrt{n-3}$) is undefined for $n<3$.
"Not estimable at this $n$" implies an $n$ was achieved.

**Fix:** replace `\FloorRho` with the DR1 statement, delete the design-target power table (`docs/method.md`
§12.6 is not an achieved-$n$ table), rewrite conclusion item 4.

### F3. iSys scope: the IS/DSR framing is cosmetic, and this is measurable.

V3 quotes the desk-rejection reason: manuscripts that *"treat information systems as a synonym for software
systems, applications, or technical computing artifacts"*. This one does, while asserting the opposite.

- **0 of 78** `refs.bib` entries are IS venues — no MISQ, ISR, EJIS, JSIS, I&M, DSS, JIT, iSys, SBSI,
  GranDSI, EnANPAD. Journals are EMSE (11), TSE (7), SQJ (4), TOSEM (2). V6 requires *"proper coverage of
  SOL (SBC OpenLib) literature"*; V7 names the venues. Neither appears.
- **DSR is invoked twice, cited zero times.** `02-background.tex:71` (*"in the sense of Design Science
  Research (DSR)"*) and `04-design.tex:23` (*"the design-science convention"*) carry no citation; `refs.bib`
  has no Hevner, Peffers, March & Smith, Wieringa or Gregor DSR source. V5 calls DSR *"particularly common"*
  at iSys and requires the rationale and evaluation *"clearly described"*. Invoking the journal's house
  methodology with zero sources in it is the clearest tell of retrofitting.
- **The IS definition is uncited.** `02-background.tex:6–11` (*"In the IS tradition an information system is
  understood as a system of work…"*) and the next paragraph carry no citation; `01-introduction.tex:6–8`
  asserts *"an old concern of the Information Systems (IS) field"* with none.

Against V2 (*"technology as a means rather than an end, emphasizing the phenomena that arise from its
development, adoption, and use across organizational and social contexts"*), the paper's empirical content —
screening yields, build failures, tool pinning — is the means, and no organisational phenomenon is observed.
V4 lists *"Programming techniques or frameworks"* as out of scope. A desk editor reads "mutation-based
instrument" + "2,552 repositories" in the abstract and stops.

**Fix:** 8–12 IS sources doing real work (business–IT alignment, requirements traceability, IS success, DSR),
at least two from SOL/iSys/SBSI, cited at the claim; one DSR source per DSR claim; reframe DK as an
IS-governance instrument for a named stakeholder (audit, compliance, contractual acceptance —
`04-design.tex:6–11` gestures at this then drops it); move PIT/Stryker/operator detail to an appendix, since
that detail is what makes the paper read as SE.

---

## 2. Overclaims

1. **Abstract is 262 words** (257 excluding the five `[…]` labels) against V12's *"150–250 words"*. One
   paragraph and structured — both fine. Must fix; a desk-review checkbox.
2. **No limitation sentence in the abstract.** `docs/method.md:303` says the paper *"**must** state which
   [rater] design was used, in the method section and in the abstract's limitation sentence."* Neither
   exists; the rater problem is unmentioned in the abstract.
3. **`06-results.tex:131–136`: "zero mutants in the `NO_COVERAGE` category … the tool was able to distinguish
   executed but survived from never executed."** A zero count in one bin cannot demonstrate discrimination
   between bins; `RUNLOG` R001/R002 report 0 because the toy suites cover all of `pricing.js`. Fix: cite the
   tool's distinct `NoCoverage` status in `results/pilot/smoke-js-mutation.json`, or add an unexercised
   control module.
4. **`06-results.tex:138–140`, `08-threats.tex:118–119`, `09-conclusion.tex:22–25` present "the same domain
   logic" 19 vs 43 as clean cross-tool incomparability.** Confounded: `RUNLOG` R002 records
   `operators = PIT DEFAULTS (probe only)`; Stryker ran its default set. The only variable the comparison
   isolates — the tool — is contaminated by operator set, and `05-method.tex:188–192` mandates a restricted
   decision-logic set with *"no operator set was altered after seeing results"*, so the feasibility runs
   contradict the method's own mutation protocol. Fix: print both operator sets in Table 3; downgrade to
   "PIT DEFAULTS vs Stryker defaults".
5. **Two frequency/generalisation claims exceed the design.** `07-discussion.tex:11–13`: *"A high overall
   mutation score with a near-zero differential is a common and previously invisible configuration"* —
   "common" from $n=0$. `main.tex:82–83`: *"public BDD suites are overwhelmingly frameworks, templates and
   demonstrators"*, though the unit was repositories carrying a BDD **topic tag**, which the paper itself
   calls *"an unreliable indicator of BDD use even at the level of file presence"* (`06-results.tex:49–50`).
   Fix: "a configuration that a differential measurement would make visible"; "public repositories that
   self-identify as BDD".
6. **The novelty conjunction is defended, not tested.** `03-related.tex:105–111`: *"The claim this paper
   defends is a conjunction of four elements"* — corpus scale, domain restriction, differential kill,
   longitudinal. Zero measured. `lit/novelty.md:108–110`: *"If the pilot shows any one of them is
   unmeasurable, the honest response is to narrow the paper's claim … not to keep the claim and drop the
   measurement."* All four were dropped and the claim kept.
7. **The negative existence claim rests on an admitted-incomplete search.** `01-introduction.tex:49–51`
   (*"no study has measured…"*), `03-related.tex:95–97`. `lit/novelty.md:84–94` records **Mughal 2026 (347
   repositories, 23,667 feature files, 1.1 M steps)** and Sohn 2025 excluded by a Crossref-DOI-only rule, and
   that *"Portuguese-language venues (SBES, CBSOFT, SBC) could not be swept because DBLP is bot-blocked."*
   For a Brazilian IS journal this is a direct V6 failure. Fix: state search scope beside every novelty
   claim; write "we found no peer-reviewed study that…".
8. **Unperformed pre-registered work is described as done.** `10-declarations.tex:37`: *"seeded-drift
   experiments were confined to separate copies so that no measured artefact was modified"* — no injection
   campaign exists (no `work/injections/`, nothing in `RUNLOG`). `PROTOCOL.md` §8 lists *"Seeded-drift
   validation — known drift injected into a working suite…"* among things *"the accompanying study reports"*;
   practitioners will read that as a validated instrument. And RQ1's promised *"seeded-drift detection rate"*
   (`04-design.tex:99–101`, falsifiable per `docs/method.md:23` at sens ≥0.80 / spec ≥0.90) is absent from
   results and from `06-results.tex:186–202`'s five-item inventory of what could not be measured — although
   it needs no humans and no builds, only a suite that runs, and the paper had two. Fix: delete the
   declarations clause; rewrite `PROTOCOL.md` §8 in the conditional; run the experiment on both harness
   suites or list it.
9. **78 vs 70 references.** `RUNLOG` R004 claims *"78 entries … 78/78 PASS"*; only 70 keys are cited and 8
   bib entries never are (`Guerino2024PythonTools`, `Martins2024TestRefactoring`,
   `niedermayr2016willmytests`, `roman2020tddm`, `rwemalika2023suit`, `Sanchez2022MutationInTheWild`,
   `shrestha2011assertionsoracles`, `vigano2022damat`). V14 requires correspondence *"vice versa"*. Two of
   the eight are on-topic and belong in the text: `niedermayr2016willmytests` is the nearest precedent in
   `lit/novelty.md:28`, and `shrestha2011assertionsoracles` belongs in §"oracle problem".

---

## 3. Survivorship / attrition attack

Credit: counts rather than a rate (`06-results.tex:103–108`); `no_bdd_execution` separated from
`build_fails`; Table 2 sums correctly (0+6+8+1+10 = 25). Six problems remain.

1. **The 25-of-94 selection rule is undisclosed.** Nothing in the paper or `docs/method.md` says *which* 25
   were attempted or by what rule. It is the paper's only empirical sample; without the rule it is
   uninterpretable. Fix: state it, with draw indices.
2. **23 "screened" repositories were never screened.** `SCREENING.json` records `fetch_failed_413: 23`; in
   `candidates.csv` those rows have blank `archive_bytes` and `n_files`. HTTP 413 = payload too large, so
   missingness is **correlated with size**, hence with application shape and domain layer.
   `06-results.tex:30` prints `\Nscreened` at *"100.0 %"* and Table 1's caption claims *"Every screened
   repository is counted exactly once"* — false for those 23, which include `reqnroll/Reqnroll`,
   `cucumber-rs/cucumber`, `salesforce/codeceptjs-bdd`, `IBSCorp/Chameleon`: the profile wanted. Fix: move
   them out of the denominator (94/2,529 = 3.72 %), report as non-retrievable, state the bias direction.
3. **Census-vs-sample incoherence.** `05-method.tex:30–33` describes a *"hash-ordered permutation … with fixed
   seed"*; `06-results.tex:17` reports **all** 2,552. In a census the permutation is inert and the *"95 %
   Wilson interval 3.0–4.5 %"* is not a sampling interval. (Arithmetic verified: 94/2,552 → Wilson
   3.02–4.49 %, so the numbers are right and the interpretation is not.) Fix: pick one identity.
4. **The evidence log contradicts the manuscript.** `RUNLOG` R005: *"build/execution screen: **18
   attempted**, 0 green"*. `numbers.tex:20` says 25; the CSVs also give 25. The append-only log is stale by
   seven attempts and will contradict the PDF inside the package. Fix: append R006 with final counts; never
   edit R005.
5. **The `no_bdd_execution` and `bdd_fails` bins are misclassified, and "0 green" depends on it.** All 8
   `no_bdd_execution` rows carry reason `no_tests_found`, not the stated meaning.
   `NaturalIntelligence/cytorus`'s `log_tail` shows *"√ should filter based on the include / 1 passing
   (43ms)"* — a scenario that appears to have run and passed, binned as not executed. Two of six `bdd_fails`
   show multi-module Maven reactor failures (`-rf :cukes-core`, `-rf :example-cucumber`), not *"failing
   scenarios at HEAD"* as Table 2's column asserts. And `bdd_evidence` is **empty for every `bdd_fails`
   row**, contradicting `05-method.tex:85–86` (*"the harness requires positive evidence of Cucumber
   execution"*). Fix: hand-adjudicate the 24 non-`unsupported` rows, publish per-row evidence, flag the
   ambiguous ones.
6. **Nothing static was analysed, though all of it was obtainable.** The screening pipeline parsed features
   for the whole frame: `candidates.csv` carries `n_features`, `n_scenarios`, `n_step_files`, `n_app_sources`
   for all 2,552 rows — **16,143 scenarios across the 94 eligible** repositories. D1, D2, D4, D5, D6 are
   static; `data/repos/` holds **96 working copies**. No indicator distribution is reported anywhere.
   `numbers.tex:9` explains the history zero as *"No repository in the corpus yielded a usable series"* — a
   claim about the corpus that is actually a protocol consequence: all 16 git clones are
   `git clone --depth 1` (verified: every one has exactly 1 commit), and `docs/method.md` §13.1 requires
   `git log` walks. Fix (highest-value repair in the paper): report D1/D4/D5/D6 over the 94; state the
   depth-1 incompatibility as the reason history did not run (or re-clone — static, no builds); replace the
   corpus-blame caption.

**What a reviewer will demand:** the 25-of-94 rule; the 23 unretrieved units out of the denominator with a
bias statement; a hand-adjudicated build-screen table with per-row evidence; and descriptive static
indicators on the 94. With those four it is defensible; without them the population claim is about the
authors' execution budget, not about GitHub.

---

## 4. Mutant representativeness

The refusal to fabricate an agreement statistic is right and well argued (`08-threats.tex:39–47`,
`06-results.tex:187–192`): *"an automated agreement statistic would measure the consistency of a heuristic
with itself."* I would not change a word. But "no raters" closes a question that had two cheaper,
pre-registered, non-rater answers, both skipped without mention:

- **I4, the business-constant perturbation probe** (`docs/method.md:272`, §10.3): change one threshold,
  *"the suite must FAIL"*; called *"the strongest available validity evidence for (or against) the mutant
  proxy"*. It needs a runnable suite, not a rater. With 0 green it could not run — but the paper never says
  so, so the gap reads as an omission rather than a consequence.
- **Invalid-mutant counts** are required unconditionally (§8.5: *"its count is always reported"*). None
  appear.

"Business-rule relevance" is *defined* by the paper's own rule set (`05-method.tex:180–186`) and the D7 loose
census is implemented; the paper says it reports D7 "as an automated census" and prints no value. So the
defence is not "we could not measure" but "we did not report the unvalidated measurement we made." Fix: link
the I4 omission to the zero-green failure; print the D7 census and invalid counts with the precision caveat;
invoke the §11.4 intra-rater fallback or say in one sentence why even that failed.

---

## 5. Construct validity

Credit: the snapshot/drift separation is handled better than in most papers I review.
`01-introduction.tex:69–76` defines oracle strength as a snapshot property and drift as change over time;
`08-threats.tex:90–100` bans "trend" and "rate" for two-snapshot comparisons; `docs/method.md` §1.2 anchors
the same distinction. No violation found in the prose. Two gaps:

1. **The seven "drift indicators" are static states.** `docs/method.md:16` warns *"a static indicator is
   **not** evidence of change; it is a state that predicts weakness"*, yet `05-method.tex:136` calls them
   drift indicators and `06-results.tex:163–164` asks *"whether drift accumulates"* in the same breath. Fix:
   rename to weakness/drift-risk indicators, or add one sentence at first use.
2. **The specialisation is asserted, not argued.** `03-related.tex:98–100` calls specification drift *"a
   specialisation of architectural drift"*. Architectural drift is structural divergence; oracle weakness is
   functional. A suite can drift structurally while staying oracular, and weaken with no structural change.
   Fix: two sentences on what the specialisation preserves, or call it an analogy.

---

## 6. Coverage confounding and BDD attribution

Best-constructed argument in the paper: coverage conditioning quoted verbatim (`05-method.tex:107–115`),
`\mscov` primary, `DK_norm` on a common mutant set (`05-method.tex:117–132`), causal reading refused three
times (`08-threats.tex:66–88`). No complaint about the logic.

The containment the differential rests on is declared, not tested. `05-method.tex:117–119`: *"Formally the
protocol asserts $\mathit{executed}(\bdd) \subseteq \mathit{executed}(\full)$"* — "asserts".
`docs/method.md` §8.6 makes it a *checked* assertion with three conditions, two fatal if they fail, and
requires the executed-test identifier sets to be logged. **No mode-integrity result appears anywhere**, and
condition (2) — `executed(bdd) ∩ executed(non-BDD) = ∅` — is what licenses the word "alone" in RQ2. The
claim that *"per-mutant coverage and per-scenario attribution [were] confirmed end to end"* (`main.tex:78`,
`09-conclusion.tex:12–15`) rests on `RUNLOG` narrative, not a reported assertion. Fix: one sentence in
§Tool feasibility — implemented and logged, exercised only on the two harness suites because no corpus
repository produced both modes — and soften "confirmed end to end".

---

## 7. Venue fit

See F3: the framing is rhetorically right and evidentially hollow, and V2/V4/V5/V6/V7 fail on the reference
list alone. One point specific to fit: the genuinely IS-relevant content — the interpretation rules that
forbid managerial misreadings (`05-method.tex:107–115`, `07-discussion.tex:66–83`) — is buried as a
methodological caveat instead of being the contribution. Lead with it.

---

## 8. Reproducibility attack

`10-declarations.tex:20–29` promises a full package. It is not there.

1. **`results/runlog.jsonl` does not exist**, though §15.1 makes it the 40-field append-only record and §15.3
   says `RUNLOG.md` is *"generated by `scripts/render_runlog.py` … never hand-edited"*. **That script does
   not exist either.** What exists is five prose entries for 2,552 screens and 25 builds — and the file
   contains a Windows-1252 `0x97` at offset 6433 in otherwise-UTF-8 data, so a strict decoder rejects it.
2. **No corpus commit SHAs.** `RUNLOG`'s header points to `data/corpus/LOCKFILE.csv` — **which does not
   exist**. Nothing is pinnable; no build is reproducible.
3. **The attrition dataset does not exist.** §5.4: *"`data/attrition/attrition.csv` — this log **is** the
   attrition dataset"*, 40-column header. Absent.
4. **`numbers.tex` is generated before its inputs are final** (10:25:18 vs `bs_java.csv` 10:27:32). The macros
   I first read (`\Nbuildtested{22}`, `\Nbdffails{5}`, `\Nnobddexec{7}`, no `\Nunsupported`) differ from the
   current file (25/6/8/1) — the numbers moved *during this review*. Fix: have `make_numbers.py` assert every
   input's mtime is older than the output's and fail otherwise. Five lines, and it prevents the error in §3.4.
5. **No environment manifests or per-repo logs.** §15.2 `results/env/<run_id>.json`, §15.5
   `results/logs/<repo_id>/`, the §15.4 stability probe, §8.6 integrity logs and the dry-run JSON that D4 and
   D5 depend on are all absent. `results/` holds three files.
6. **The build is not reproducible off this host.** `RUNLOG` R004 lists five build-script defects patched ad
   hoc; `DEVIATIONS.md` E5 records `latexmk` unusable and the class missing `lmodern`. And `paper/main.log`
   records *"LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right."* — **the
   shipped PDF is one pass short**, so cross-references may be stale.

What *is* reproducible, and should be said louder: `data/frame/FRAME.md` records 12 slugs, 5 filters, a
6-page cap, 252 pages, 4,048 raw rows, 2,552 unique repositories and a SHA-256 of the concatenated HTML;
`candidates.csv` carries per-repo evidence. It is the best artefact in the project.

---

## 9. Compliance checklist (`submission/VENUE-RULES.md`)

- **PASS:** V10 ≥15 pages (18) · V11 English title (`main.tex:55–57`) · V13 3–6 keywords (exactly 6,
  `main.tex:88–91`) · V15 declarations in order (CRediT → Competing → Funding → Availability →
  Acknowledgments → Ethical → References) · V16/A4 AI declaration immediately before References
  (`10-declarations.tex:41–77`) · V22 ethics (`10-declarations.tex:34–39`) · V17 double-anonymous: no names,
  emails, ORCIDs, host, repository name, `github.com/…`, `osf.io` or `4open.science` anywhere in `paper/`.
- **FAIL — V12 abstract length.** 262 words, not 150–250. One paragraph (0 blank lines) and structured:
  those parts pass.
- **FAIL — V14 reference correspondence**, reverse direction: 0 undefined citations, 8 uncited entries (§2.9).
- **FAIL — V19 presentation.** `main.log` records **13 overfull `\hbox`**, six at **roughly 258 pt** (~9 cm):
  unbreakable `\texttt{}` runs in Tables 1–2 print past the text block. Plus 2 undefined font shapes and the
  missing final pass (§8.6).
- **FAIL — V2–V7 and V24(3)**: 0/78 IS references, 0 DSR citations (F3); `lit/novelty.md:93–94` admits
  Brazilian venues unswept.
- Minor: Table 1 prints *"no BDD runner dependency 0 / 0.00 %"* (`06-results.tex:34`). A criterion that
  excluded zero of 2,552 repositories does no work; drop the row or footnote it as non-binding.

---

## Addendum: what is fine (do not churn)

The snapshot-versus-drift discipline (§5); the refusal to fabricate a κ (§4); the yield arithmetic —
94/2,552 = 3.68 %, Wilson 3.02–4.49 %, reported as 3.0–4.5; Table 2 summing to its total; clean anonymity and
an unusually candid AI declaration, including that AI was not used as a rater (`10-declarations.tex:58–63`);
the frame provenance record; consistent application of the coverage-conditioning rule in prose.

---

## Ranked actions

**Must fix:** F1 pre-registration evidence or reframe · F2 `\FloorRho` prose and DR1 · F3 IS + DSR citations
and repositioning · §3.2 the 23 unretrieved repos · §3.5 build-screen adjudication and `bdd_evidence` ·
§2.1 abstract to ≤250 words plus a limitation sentence · §2.8 the false seeded-drift statements ·
§8.1–8.3 `runlog.jsonl`, `LOCKFILE.csv`, `attrition.csv` · §8.4 freshness assertion · §8.6 final LaTeX pass
and the 258 pt overfulls · §2.9 eight bib entries.

**Should fix:** §3.4 supersede RUNLOG R005 · §3.1 the 25-of-94 rule · §3.6 D1/D4/D5/D6 on the 94 and the
depth-1 explanation · §2.7 search scope · §6 mode-integrity sentence · §2.4 both operator sets · §4 D7 census
and invalid counts · §2.3 the zero-`NO_COVERAGE` inference.

**Nice to have:** §5.1 rename the indicators · §5.2 architectural-drift specialisation · §9 zero-count row ·
§2.5 "common and previously invisible".
