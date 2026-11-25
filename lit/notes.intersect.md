# intersect — literature notes (S1-D)
Facet: mutation testing × BDD/Gherkin/acceptance suites; oracle strength of acceptance tests; differential contribution of test levels; domain-layer mutation. Host date: 2026-11-25.

## NOVELTY VERDICT

**STATUS: SURVIVES — with narrowed, carefully-worded novelty.** A peer-reviewed study **has** mutation-scored a BDD acceptance suite once, on a single industrial proof-of-concept (dos Santos et al. 2024, AAT4IRS: 79% of generated mutants detected, with a hand-listed set of domain mutants). Mutation testing of Cucumber suites is also now a shipped *tool* capability (StrykerJS-CucumberJS, CucumberSwift 2026). What remains unclaimed is the **measurement at corpus scale over time**: no study scores public BDD repositories, none separates the mutants killed by the Gherkin layer from those killed by the rest of the suite, none tracks that score across repository history, and none validates drift indicators against it. **No paper found that kills the project; but the "no one has ever mutation-tested a BDD suite" phrasing is now FALSE and must not be used.**

| Question | Answer | Evidence (papers actually opened) |
| :--- | :--- | :--- |
| **Q1.** Does any published work measure mutation score of Cucumber/BDD suites **on public repositories**? | **ON PUBLIC REPOSITORIES: NO. AT ALL: YES — exactly once.** dos Santos et al. 2024 (AAT4IRS) apply mutation testing "to measure [the] effectiveness" of a BDD acceptance-test approach and report **79% of generated mutants detected** — but on a single industrial pick-and-place proof-of-concept, with a hand-written mutant list, no public corpus, no replications. Otherwise: an industrial *proprietary* Ruby project (Li et al. 2015) and two *tools* with no corpus study (StrykerJS-CucumberJS; CucumberSwift). | `santos2024aat4irs` (**the closest prior work**); `li2015mutationpracticeruby`; `binamungu2023mapping` (166 BDD papers, 2006–2021, **the string "mutat" occurs zero times in the full text** — our own check on the arXiv preprint); `yandrapally2021maewu` and `leotta2023mutta` mutate E2E suites but **not** BDD/Gherkin-scoped. |
| **Q2.** Does any work separate mutants killed by the BDD/Gherkin layer from those killed by the rest of the suite ("differential kill")? | **NO** for BDD — including AAT4IRS, which scores the whole acceptance suite as one unit. **YES in spirit, one level up:** Niedermayr et al. 2016 explicitly split unit-test and system-test suites and showed the pseudo-tested ratio "is acceptable for unit tests but not for system tests". That is test-level differential mutation analysis — extreme mutation, Java, no Gherkin. | `niedermayr2016willmytests`; `veraperez2018pseudotested` (28K+ methods). Our differential must be framed as **BDD-layer-vs-rest**, not as "first differential analysis by test level". |
| **Q3.** Does any work study how such a score **CHANGES over repository history**? | **NO for BDD.** AAT4IRS is a single snapshot. Longitudinal mutation studies exist, all non-BDD and all unit/code-level: mutant *relevance* degradation (52% of 143,500 mutants) across 4 Java systems (Ojdanić 2023); mutation coverage across 11 versions of 3 OSS Java systems (Akour & Alenezi 2020); test/production co-evolution over 526 repos with no fault-based measure (Miranda 2025). | `ojdanic2023longstanding`; `akour2020evolution`; `miranda2025coevolution`. Ojdanić 2023 is the paper to cite as "the closest longitudinal mutation work" — and to differentiate from. |
| **Q4.** Does any work validate drift/decay indicators against **mutation score as ground truth**? | **NO.** Drift indicators for BDD exist and are validated against *co-change*, not fault detection: Yang et al. 2019 predict when a `.feature` file must change (79% accuracy, AUC 0.77) with no ground-truth fault measure. BDD quality work (Oliveira 2019; Binamungu 2018a/2018b) is checklist/structural, never fault-validated. | `yang2019cochanges`; `oliveira2019howtoevaluate`; `binamungu2018duplicate`; `binamungu2018maintaining`. |

### What exactly remains novel (defensible four-part claim)
1. **Corpus-scale, public-repository** mutation scoring of BDD suites. AAT4IRS proves the *method* works on one industrial system; nobody has done it across public repositories.
2. **Domain-layer restriction** of mutation (business logic, not glue/infrastructure). AAT4IRS's mutants *are* domain-level, but they are **hand-written for one robot task** (a table of a few named mutants); automating domain-layer mutant selection and applying it uniformly across a corpus is unclaimed. No other retrieved work restricts mutation analysis to a business layer — closest concepts are specification-level mutation (Black et al. 2000) and data/interface-level mutation (Viganò et al. 2022; Yandrapally & Mesbah 2021).
3. **Differential kill**: mutants killed by the Gherkin layer vs. the remainder of the suite. Unclaimed for BDD; one precedent at unit-vs-system granularity (Niedermayr 2016).
4. **Longitudinal erosion** of that score, plus validation of drift indicators against it as ground truth. No precedent found.

### Gap statement (one paragraph, conservative)
> To our knowledge, no study has measured how the mutation-based oracle strength of public Behaviour-Driven-Development suites evolves, nor separated the mutants killed by the specification layer from those killed by the rest of the suite. Mutation testing has been applied to acceptance-level suites before: once to an industrial Ruby project at Medidata (Li et al., 2015), once to a BDD acceptance suite for a single industrial robotic proof-of-concept, where 79% of a hand-written set of domain mutants were detected (dos Santos et al., 2024), and to E2E/UI web suites evaluated on six public web apps (Yandrapally & Mesbah, 2021) and two web applications (Leotta et al., 2023); test-level differentials have been measured by splitting unit from system suites under extreme mutation (Niedermayr et al., 2016; Vera-Pérez et al., 2018). All of these are single snapshots, none is scoped to Gherkin scenarios across a corpus, and none separates the specification layer's contribution. Conversely, the BDD literature measures specification quality structurally or qualitatively (Oliveira et al., 2019; Binamungu et al., 2018a, 2018b) and predicts specification drift from co-change signals without fault-based validation (Yang et al., 2019); the most recent systematic mapping of 166 BDD studies identifies an "acute shortage of metrics for measuring various aspects of BDD specifications" and does not mention mutation analysis at all (Binamungu & Maro, 2023). Longitudinal mutation work exists only for code-level mutant suites, where 52% of 143,500 mutants lose relevance over time (Ojdanić et al., 2023) and mutation coverage has been tracked across 11 versions of three Java systems (Akour & Alenezi, 2020). Our study connects these two lines: it uses mutation score as ground truth for the oracle strength of public BDD suites, isolates the BDD layer's contribution, and measures how that contribution erodes as specifications drift.

### Threats to the verdict, stated plainly
- **AAT4IRS (2024) is the paper a reviewer will cite against us.** Framing rules: (a) never say "no study has mutation-tested a BDD suite"; (b) say "a single industrial proof-of-concept, not a corpus, not longitudinal, not layer-separated"; (c) note that its mutants are hand-listed for one pick-and-place task, so the result does not generalise or scale. **Get its full text before submission** (Frontiers is open access) to confirm whether the mutants are manual and how many there are — the abstract alone does not say.
- **Closest older prior work, and what could not be verified.** Li et al. (2015): abstract says only "an industrial Ruby project at Medidata"; the authors' Mutation-2015 slides (opened: `https://mutation-workshop.github.io/2015/mutationTestingInPractice.pdf`) never mention Cucumber or BDD. The paper's Crossref reference list does cite "Behavior driven development for Ruby" (Chelimsky, 2009) and a statement-coverage tool — suggestive, **not** evidence that the scored suite was Cucumber. **Do not claim in the paper that Li et al. scored a Cucumber suite.**
- **Practice vs measurement.** CucumberSwift (2026) documents a `mutation-test` command that attributes each mutant to the scenarios that would catch it (`killedBy` / `coveredBy`), computes a per-feature `Mutation` score, and writes Stryker-format reports; `@stryker-mutator/cucumber-runner` makes StrykerJS drive CucumberJS. The *practice* is not novel and reviewers may say so; the **corpus-scale longitudinal measurement and the drift validation are**.
- Search coverage limits are listed at the end; DBLP and IEEE Xplore were not directly searchable (see §Search log).

---

## Scope searched
Queries (web_search + arXiv HTML search + OpenAlex + Crossref bibliographic + Semantic Scholar Graph):
`mutation testing cucumber`; `mutation analysis BDD`; `mutation testing behavior-driven development`; `mutation testing executable specifications Gherkin`; `mutation score acceptance tests empirical`; `mutation testing system tests`; `mutation testing end-to-end tests`; `mutation testing GUI tests`; `mutation analysis acceptance test suites fault detection`; `mutation testing integration tests`; `Stryker cucumber`; `PIT cucumber`; `mutmut behave`; `teste de mutação BDD`; `mutação cenários`; `mutation testing feature files scenarios`; `mutation testing acceptance criteria business rules layer`; `unit tests versus system tests fault detection`; `test pyramid empirical`; `test suite effectiveness degradation over time`; `co-evolution production and test code`; `test suite evolution test smells`; `oracle strength`; `test oracle quality acceptance`; `domain mutation`; `specification coverage business rules`; plus Crossref/Unpaywall/S2 lookups for every DOI.
Databases hit: Crossref REST (via web_fetch), OpenAlex, Semantic Scholar Graph (via web_fetch), Unpaywall (via web_fetch), arXiv HTML search, publisher/DOI landing pages, GitHub raw, npm/PyPI pages for tool evidence.
Date searched: 2026-11-25.

## Papers opened

### santos2024aat4irs — AAT4IRS: automated acceptance testing for industrial robotic systems (Frontiers in Robotics and AI 2024) ⚠️ CLOSEST PRIOR WORK
- **What it does:** Proposes a BDD-based acceptance-testing approach for industrial robotic systems: features/scenarios written in natural language to describe business requirements ("BRs"), executed as automated acceptance tests.
- **Method / data:** Proof-of-concept on a pick-and-place robotic process; **mutation testing used to measure the approach's effectiveness**, with a hand-listed table of domain-level mutants (e.g. "change the y-value in translation", "do not change the gripper status", "change the gripper status twice").
- **Key findings (verbatim):** "We evaluated our ST approach through a proof-of-concept, performing a pick-and-place process and applying mutation testing to measure its effectiveness. The results show that the test suites implemented using AAT4IRS were highly effective, with 79% of the generated mutants detected".
- **What it does NOT answer for us:** one industrial system, no public repositories, no corpus, no repetition; a small hand-written mutant list rather than an automated domain-layer operator set; the whole acceptance suite is scored as one unit (no BDD-vs-rest separation); single snapshot (no history); no drift indicator validated.
- **Threat it poses to our novelty:** **MAJOR** — it removes the claim "nobody has mutation-tested a BDD/acceptance suite". It leaves intact every quantitative, corpus, differential and longitudinal claim.
- **Action for the Lead:** obtain the open-access full text (Frontiers) and extract (a) how many mutants, (b) whether mutants were applied to the application code or to the scenarios, (c) what "generated mutants" means there. The abstract alone does not say.

### li2015mutationpracticeruby — Mutation testing in practice using Ruby (ICSTW / Mutation 2015)
- **What it does:** Devises eight Ruby mutation operators and applies mutation testing to an industrial Ruby project at Medidata; reports lessons for adopting mutation testing in agile practice.
- **Method / data:** 8 subjects inside one proprietary product; existing test sets plus newly written mutation-adequate tests; Amazon EC2 to parallelise mutant runs. Numbers below are from the authors' Mutation-2015 slides (paper paywalled at IEEE): 1,716 mutants, mean original mutation score 0.78, 38 mutation tests added, 31 equivalent mutants, mean statement coverage 97.2%.
- **Key findings (verbatim numbers only):** 1,716 mutants total; mean MS-Original 0.78; mean MS-All 0.99 (slides, Table "Results").
- **What it does NOT answer for us:** proprietary single project (not public repos); no BDD/Gherkin scoping (unverified — see threats); no per-layer attribution; no history.
- **Threat it poses to our novelty:** **minor–major** — it is the only "mutation testing of a real project's acceptance-ish tests" paper, and the closest prior work; but it is a single industrial case study with no corpus, no differential and no longitudinal axis.

### li2016skyfire — Skyfire: Model-Based Testing with Cucumber (ICST 2016)
- **What it does:** Generates Cucumber scenarios from UML behavioural models to replace hand-written ones.
- **Method / data:** Tool + industrial case study at Medidata.
- **Key findings:** states that hand-written Cucumber scenarios "are usually weak" and that "practitioners do not have a metric to measure test coverage".
- **What it does NOT answer for us:** proposes no oracle/fault-based metric; covers graph coverage of the *model*, not the fault-detection strength of the suite.
- **Threat:** **none** (it is motivation, not competition).

### niedermayr2016willmytests — Will my tests tell me if I break this code? (CSED 2016)
- **What it does:** Uses extreme mutation (method-body removal) to find "pseudo-tested" methods in OSS Java projects and asks whether coverage is a valid effectiveness proxy.
- **Method / data:** Extreme mutation over open-source Java projects; pseudo-tested ratio per suite type.
- **Key findings (verbatim):** pseudo-tested ratio "is acceptable for unit tests but not for system tests (that execute large portions of the whole system)"; therefore "the coverage metric is only a valid effectiveness indicator for unit tests".
- **What it does NOT answer for us:** Java/unit-method artefacts; extreme mutation, not domain-layer mutation operators; suites split unit-vs-system, not BDD-vs-rest; no public *BDD* corpus; no history.
- **Threat it poses to our novelty:** **MAJOR** — this is the precedent for "mutation-based adequacy differs by test level". Our claim must be BDD-layer-specific, not "first to differentiate by test level".

### veraperez2018pseudotested — A comprehensive study of pseudo-tested methods (EMSE 2018)
- **What it does:** Replicates Niedermayr at scale (28K+ methods) and characterises 101 pseudo-tested methods manually.
- **Key findings:** pseudo-tested methods exist in all subjects and are "significantly less tested than the other methods; yet, for most of them, the developers would not pay the testing price to fix this situation".
- **What it does NOT answer for us:** method-level, Java, unit suites; no acceptance/BDD level; no longitudinal erosion measure.
- **Threat:** **minor** — it shows the oracle-weakness phenomenon is real and measurable, which supports our premise but not our specific claim.

### yandrapally2021maewu — Mutation Analysis for Assessing End-to-End Web Tests (ICSME 2021)
- **What it does:** MaewU mutates the dynamic DOM in the browser rather than source code; 16 operators derived from 250 bug reports; evaluated on **six open-source web apps**.
- **Key findings:** the framework is effective for assessing UI test suites' adequacy and supports suite improvement.
- **What it does NOT answer for us:** mutation target is DOM behaviour/appearance, not business logic; no Gherkin/BDD scoping; no separation of BDD-layer kills; no history.
- **Threat it poses to our novelty:** **MAJOR** — "mutation analysis of acceptance-level (E2E/UI) suites on public repositories" already exists. We cannot claim to be first to mutate suites above unit level, nor first to do so on public repos.

### leotta2023mutta — Mutta: a novel tool for E2E web mutation testing (SQJ 2023)
- **What it does:** Automates whole-app mutation for E2E suites (server + client), then compares two oracle styles — classical assertions vs differential testing.
- **Key findings:** >15k mutants, ~87k test runs, 2 web applications; Mutta is usable to compare the effectiveness of differently-built E2E suites.
- **What it does NOT answer for us:** two applications, oracle *style* comparison rather than oracle strength per specification unit; no BDD layer isolation; no time dimension.
- **Threat:** **major for facet 3 (oracle strength of acceptance tests)** — the "compare acceptance-test oracle styles under mutation" idea is taken. Our angle must be *specification-level* oracle strength and its erosion, not oracle-style comparison.

### vigano2022damat — Data-Driven Mutation Analysis for Cyber-Physical Systems (TSE 2022)
- **What it does:** Mutates data exchanged between components (rather than code) to assess CPS test suites for interoperability faults; applied to microsatellite/nanosatellite software.
- **Key findings:** "effectively detects test suite shortcomings, is not affected by equivalent and redundant mutants, and entails acceptable costs".
- **What it does NOT answer for us:** black-box/data-level mutation; no domain/business layer selection in our sense; no BDD; no public corpus.
- **Threat:** **minor** — establishes that "mutate the interface, not the code" is an accepted system-level idea; useful precedent for defending domain-layer mutation.

### ojdanic2023longstanding — Keeping Mutation Test Suites Consistent and Relevant with Long-Standing Mutants (ESEC/FSE 2023)
- **What it does:** Measures how mutant suites degrade as code evolves; introduces a mutant brittleness measure; identifies long-standing mutant suites.
- **Key findings (verbatim):** "We measure this degradation in relevance for 143,500 mutants in 4 non-trivial systems, finding that 52% degrade, on average."
- **What it does NOT answer for us:** mutant *relevance*, not test-suite oracle strength; Java systems; no BDD/Gherkin; no drift-indicator validation.
- **Threat it poses to our novelty:** **major for the longitudinal wording** — "mutation results degrade over time" has been said. Our claim must be "the oracle strength *of the BDD layer* erodes", and we must cite Ojdanić as the source of the general phenomenon.

### andrews2005ismutation — Is mutation an appropriate tool for testing experiments? (ICSE 2005)
- **Key findings:** mutants are "similar to real faults" and mutation is trustworthy for experiments; hand-seeded faults are harder to detect than real faults.
- **Why it matters:** defence for using mutation score as ground truth (RQ4).
- **Threat:** none.

### jia2011survey — An Analysis and Survey of the Development of Mutation Testing (TSE 2011)
- **What it does:** Survey of three decades of mutation testing.
- **Why it matters:** citable baseline that the field is code/unit-centric.
- **Threat:** none.

### barr2015oracleproblem — The Oracle Problem in Software Testing: A Survey (TSE 2015)
- **What it does:** Surveys oracle automation (modelling, specifications, contracts, metamorphic) and the residual human oracle.
- **Why it matters:** the canonical framing of "oracle strength" as a problem; supports our RQ framing that oracles are rarely *measured*.
- **Threat:** none (it proposes no BDD measurement).

### binamungu2018maintaining — Maintaining BDD specifications: challenges and opportunities (SANER 2018)
- **What it does:** Surveys 75 BDD practitioners from 26 countries on BDD benefits and maintenance pain.
- **Key findings:** BDD specifications "suffer the same maintenance challenges found in automated test suites more generally"; 10 research opportunities proposed.
- **What it does NOT answer for us:** perceptions, not measurement; no fault-based oracle evaluation.
- **Threat:** **none for novelty; strong for motivation** — it is the empirical warrant that BDD specs drift.

### binamungu2018duplicate — Detecting duplicate examples in BDD specifications (VST 2018)
- **What it does:** Dynamic-tracing approach to detect duplication in BDD example suites; evaluated on **three open-source systems**.
- **What it does NOT answer for us:** structural redundancy, not oracle strength; no link to fault detection.
- **Threat:** **minor** — it is the existing "quality metric for BDD suites on public repos", so we must position our metric against it.

### binamungu2023mapping — Behaviour driven development: A systematic mapping study (JSS 2023)
- **What it does:** Maps 166 BDD papers (2006–2021) across venues, contributions, evaluation methods and themes.
- **Key findings:** "acute shortage of metrics for measuring various aspects of BDD specifications and the processes for producing BDD specifications"; future research should give metrics "due attention".
- **Independent check performed:** converted the arXiv preprint (2305.05567, submitted version of the JSS article) to text and searched it — **zero occurrences of "mutation" or "mutant"**; one occurrence of "oracle" and that only in a cited title about *generating* oracles from NL requirements.
- **What it does NOT answer for us:** it is a map, not a measurement.
- **Threat:** **none — it is our strongest supporting citation for the gap.**

### oliveira2019howtoevaluate — How to Evaluate BDD Scenarios' Quality? (SBES 2019)
- **What it does:** Derives quality attributes from interviews with 18 practitioners and proposes a question-based checklist for BDD scenario quality.
- **What it does NOT answer for us:** no operational/fault-based validation; no coverage of "identifiable business rule".
- **Threat:** **minor** — occupies the "quality of BDD scenarios" niche qualitatively; leaves the quantitative, fault-based niche open.

### yang2019cochanges — Predicting Co-Changes between Functionality Specifications and Source Code in BDD (MSR 2019)
- **What it does:** NLP-based identification of feature-file/code co-changes (79% accuracy) and a random-forest predictor of when a `.feature` file should be modified (AUC 0.77).
- **Key findings (verbatim):** "Therefore, .feature files can be out-of-date, reducing the advantages of using BDD."
- **What it does NOT answer for us:** the predictor is validated against *observed co-changes*, never against whether stale specs still detect faults.
- **Threat it poses to our novelty:** **major for RQ4 framing** — this is the drift indicator we would validate against mutation score. We must cite it as the state of the art we improve on, and we must not claim to be first to *predict* BDD drift.

### soto2021e2edataset — A dataset of regressions in web applications detected by end-to-end tests (SQJ 2021)
- **What it does:** 6 manually injected regressions in 3 Java/Spring web apps plus tooling; compares E2E vs unit datasets.
- **Key findings:** E2E tests consume far more time/resources than unit tests.
- **Why it matters:** justifies not executing whole E2E suites at corpus scale; supports a static/mutant-targeted design.
- **Threat:** none.

### titcheuchekam2017faultrevelation — Mutation, statement and branch coverage fault revelation (ICSE 2017)
- **Key findings:** "strong mutation testing has the highest fault revelation of four widely-used criteria"; fault revelation rises only at high coverage.
- **Why it matters:** the empirical basis for treating mutation score as the strongest available fault-revelation proxy (our ground truth).
- **Threat:** none.

### akour2020evolution — Test suites effectiveness evolution in open source systems (IJEECS 2020)
- **What it does:** Measures code coverage, suite LOC and **mutation coverage** across 11 versions of 3 OSS Java systems.
- **Key findings:** test size does not reliably correlate with effectiveness; correlation between effectiveness, size and coverage is weak.
- **What it does NOT answer for us:** unit level; code coverage-centric; no BDD; no per-layer attribution.
- **Threat it poses to our novelty:** **major for the longitudinal wording** — "mutation coverage tracked across versions of OSS systems" already exists. Our novelty is that it is tracked for the **BDD layer** and used to validate **drift indicators**.

### miranda2025coevolution — Test Co-Evolution in Software Projects (JSEP 2025)
- **What it does:** 526 GitHub repos, 6 languages; clusters test/production co-evolution patterns.
- **Key findings:** 5 distinct test-evolution patterns; high co-evolution correlates with smaller teams; no relation to maintenance-activity type.
- **What it does NOT answer for us:** measures *synchrony of change*, never whether the tests still detect faults.
- **Threat:** **minor** — the largest longitudinal test-evolution study, so our corpus-scale claim must be about oracle strength, not about "studying test evolution at scale".

### roman2020tddm — Test-driven development with mutation testing (SQJ 2020)
- **What it does:** Controlled experiment (22 students) comparing TDD+M with TDD, cross-running each group's tests on the other's code.
- **Key findings:** 53.3% vs 33.5% statement coverage and **64.9% vs 37.5% mutation coverage**; more post-release defects found.
- **Why it matters:** precedent for mutation coverage as the primary outcome measure of suite quality.
- **Threat:** none (unit level, students).

### black2000specmutation — Mutation operators for specifications (ASE 2000)
- **What it does:** Defines mutation operators for formal specifications to generate test suites; analyses fault classes detected.
- **Why it matters:** the canonical "mutate the specification" line — must be distinguished from our "mutate the code to grade the specification's oracles".
- **Threat:** **minor** — a reviewer may conflate the two; the introduction must disambiguate.

## Search log
- `mutation testing cucumber` → 10+10 screened → 2 opened (CucumberSwift docs, StrykerJS docs) → 0 peer-reviewed kept.
- `mutation analysis BDD / behavior-driven development` → ~60 screened → 6 opened → 3 kept (Li 2015, Li 2016, Binamungu 2023).
- `mutation score acceptance tests` / `mutation analysis acceptance test suites` → ~50 screened → 4 opened → 2 kept (Yandrapally 2021, Leotta 2023).
- `mutation testing system tests / end-to-end / GUI` → ~70 screened → 6 opened → 4 kept (Niedermayr 2016, Vera-Pérez 2018, Viganò 2022, Soto-Sánchez 2021).
- `mutation testing over time / longitudinal / test suite effectiveness degradation` → ~40 screened → 4 opened → 3 kept (Ojdanic 2023, Akour 2020, Miranda 2025).
- `test oracle` / `oracle strength` / `oracle problem` → ~40 screened → 3 opened → 2 kept (Barr 2015, Titcheu Chekam 2017).
- BDD quality/co-evolution (`BDD scenarios quality`, `Gherkin smells`, `co-evolution`) → ~60 screened → 6 opened → 5 kept (Binamungu 2018 SANER, 2018 VST, 2020, Oliveira 2019, Yang 2019).
- Portuguese (`teste de mutação BDD`, `mutação cenários`) → ~15 screened → 1 opened (UnB 2020 TCC) → 0 kept as peer-reviewed (see Dead ends).
- Reference-chasing inside Binamungu & Maro 2023 (166-study map) → 12 candidate refs extracted → 6 followed.
- Total papers opened and read at abstract+ level: 25 (23 kept + 2 grey-literature items rejected); rows in `refs/verified.intersect.csv`: **23**.
- **Matrix result worth stating in the paper:** `separates_bdd_from_other_tests = no` for **all 23** verified works, and `longitudinal = yes` for only 3 (none of them BDD). That table is the novelty evidence.
- **Final targeted sweep (decisive checks):** OpenAlex `title_and_abstract.search` with AND semantics, restricted to Computer Science (field 17): `mutation gherkin` → **2** results, both 2026 theses with no DOI, both about UML-based microservice test generation (not relevant); `mutation bdd` → 18 results, of which one is `santos2024aat4irs` (found this way, after 20+ keyword searches had missed it) and the rest are Binary Decision Diagram noise. `mutation cucumber` → 729 results, **100% plant biology** (the vegetable). Conclusion: the literature is genuinely thin here, and the only peer-reviewed BDD+mutation study was found by a semantics-aware title/abstract sweep, not by keyword search.

## Dead ends (do not re-search)
- **Li et al. 2015 has no open full text.** IEEE Xplore blocks (HTTP 202), computer.org is JS-only, S2/Unpaywall report CLOSED, mutationtesting.uni.lu has no PDF. Only the authors' Mutation-2015 slide deck is open (`mutation-workshop.github.io/2015/mutationTestingInPractice.pdf`), and it never mentions Cucumber/BDD. The paper's Crossref reference list cites Chelimsky's "Behavior driven development for Ruby" — suggestive only. **The Cucumber claim in the dispatch is unverified; do not build the introduction on it.**
- **CucumberSwift `mutation-test` (2026) and `@stryker-mutator/cucumber-runner`** are tools, not studies: no DOI, not citable as literature. Keep them as *practice evidence* in the threats/validity discussion, cited as URLs, not in `refs/verified.csv`.
- **unclebob/Acceptance-Pipeline-Specification** and assorted 2026 Zenodo "conformance mutation" records: unrefereed, no venue, no DOI-grade provenance. Not citable; not evidence either way.
- **Fritz, Mesiti, Thiele, "A concise guide to good practices for automated testing…" (ECEASST 2025, DOI 10.14279/eceasst.v83.2622)** — appeared under a `mutation tests by type` snippet; opened, it is a research-software practice guide with no empirical mutation data. Dropped.
- **`A dataset of regressions … detected by end-to-end tests`** looks like a Leotta/Ricca artefact but is by Soto-Sánchez et al.; do not mis-attribute.
- **Black-box "mutation testing of agent receipt verifiers" (Zenodo, Oct 2026)** — self-published note, no review, cannot be verified as literature; ignore.
- **arXiv API (`export.arxiv.org/api/query`)** returns HTTP 429 on this host; use `arxiv.org/search/?searchtype=all&query=…` via `web_fetch` instead — that works.
- **DBLP API** is behind an Anubis bot challenge (HTTP 202 HTML); `dblp.org/search/publ/api` unusable from here. Crossref bibliographic search via `web_fetch` is the working substitute.
- **`api.crossref.org` from Python** returns HTTP 429 persistently on this host; the **same endpoint via `web_fetch` works** (different egress). Use `web_fetch` for all Crossref calls.
- **`sadil.ws` (Manchester eScholar mirror) is unreachable** (TCP timeout); the Binamungu 2020 chapter PDF could not be fetched there. Its Crossref record is `10.1007/978-3-030-49392-9_6` (XP 2020, LNBIP) — not opened, not cited.

## Coverage limitations (for the Lead)
1. **IEEE Xplore is not directly searchable from this host** (HTTP 202/empty). ICSE/FSE/ASE/ISSTA/ICSME/TSE/SQJ/SBES content was reached through Crossref, OpenAlex, Semantic Scholar and publisher landing pages. A paper that exists only as an IEEE PDF with no indexed abstract could have been missed.
2. **DBLP could not be queried** (bot challenge), so author/venue sweeps (e.g., all Mutation Workshop proceedings 2019–2026) were only partially covered via OpenAlex/Crossref.
3. **Paywalls:** Li 2015 (all venues), Yang 2019, Li & Offutt TSE 2017 (DOI not resolved in time — `10.1109/tse.2016.2628722` returned 404 at OpenAlex; **verify before citing**).
4. **ACM DL full text** is blocked for most entries (only abstracts via OpenAlex/S2), which is enough for `crossref+abstract` but not for quoting methods sections.
5. **Time-boxed:** this facet was searched for ~70 minutes of wall clock. A dedicated pass over Mutation Workshop proceedings (2019–2026) and over SBES/CBSOFT Portuguese proceedings is still worth doing by another agent.
6. **NOT opened, therefore NOT in the CSV:** Binamungu, Embury & Konstantinou, *Characterising the Quality of Behaviour Driven Development Specifications* (XP 2020, Crossref DOI `10.1007/978-3-030-49392-9_6`), and Rocha, Borba & Santos, *Using acceptance tests to predict files changed by programming tasks* (JSS 154:176–195, 2019). Both are relevant (BDD-scenario quality attributes; acceptance tests as change predictors) and both are cited inside Binamungu & Maro 2023, but I could only confirm their Crossref metadata — the texts were unreachable (`sadil.ws` TCP timeout) or not retrieved. **Someone should open these before the related-work section is written.**
