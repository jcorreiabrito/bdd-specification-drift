# bdd — literature notes (facet: BDD effectiveness & Gherkin/scenario quality)

TAG `bdd` · agent S1-A2 · host date 2026-11-25 · 17 papers opened and Crossref-verified
(`refs/verified.bdd.csv`) + 2 preprints read but not Crossref-verifiable (recorded below, §Preprints).

## NOVELTY VERDICT

**PARTIAL — the composite claim survives; three of its four ingredients are individually pre-existing.**

The claim under test (§4 of the protocol):
> "The mutation-based oracle strength of public BDD suites, and its erosion over time, has not been measured at scale."

Split into the four ingredients the protocol names:

| ingredient | status in the literature | closest paper(s) |
| :--- | :--- | :--- |
| (a) public Cucumber-style suites | **exists** | Chandorkar et al. 2022 (1,572 spec files / 23 projects); Mughal et al. 2026 preprint (23,667 `.feature` files / 347 repos / 1,113,616 steps); Zampetti et al. 2020 (50,000 projects) |
| (b) mutation analysis restricted to the domain layer | **not found for BDD** | Mutta (Leotta et al. 2024) mutates *web applications* for E2E suites, 2 apps — not Gherkin-scoped, no layer restriction |
| (c) separation of BDD-only from full-suite kill | **not found** | no paper anywhere separates Gherkin/Cucumber-driven executions from unit-level executions in a kill matrix |
| (d) longitudinal / erosion component | **exists, but not on BDD and not mutation-on-BDD** | Zampetti et al. 2020 (scenario↔code Granger causality, 20 Ruby projects, ≈37% co-evolution); Sohn et al. 2025 preprint (mutation across releases, 13 Java projects, 131,308 mutants); Kim 2020 (test-smell persistence); Rwemalika et al. 2023 (smell removal over history) |

**(a) "share of mutants the BDD suite alone kills" → NOVELTY SURVIVES.**
No paper found in any of the searches logged below runs mutation analysis on Cucumber/Gherkin
suites and reports a BDD-only kill share. The decisive negative evidence is quantitative, not
impressionistic: the 2023 *Journal of Systems and Software* systematic mapping study of BDD
(Binamungu & Maro, 166 papers, 2006–2021 — the most complete map of the field) contains
**0 occurrences of "mutation"**, 0 of "fault detect", 0 of "step definition", 0 of "smell",
0 of "longitudinal" across its 65 pages (own regex probe on the arXiv PDF, reproducible).
A second, independent secondary study (Farooq et al., IEEE Access 2023) likewise reports no
suite-level fault-detection measurement. Every BDD quality paper found measures quality by
*opinion* (Binamungu et al. 2020; Oliveira et al. 2017, 2019), by *static structure*
(Chandorkar et al. 2022), by *duplication/similarity* (Irshad et al. 2022; Mughal et al. 2026),
or by *perceived benefit* (Couto et al. 2022; Binamungu et al. 2018). None by killing mutants.

**(b) "how that changes over repository history" → PARTIALLY KILLED.**
Longitudinal mutation scoring is *not* novel in general: Sohn et al. (arXiv 2025) already track
mutants across releases and define "latent mutants" (131,308 mutants, 13 OSS Java projects,
11.2% live, 3.5% latent, 104 days mean latency). Co-evolution of BDD artefacts with production
code is also *not* novel: Zampetti et al. (2020) already measure it. What has not been done is
tracking **BDD-attributable** kill over history — i.e. whether the same suite's Gherkin-driven
assertions stop catching the behavioural mutants they used to catch. That is our claim, and it is
unclaimed, but a reviewer familiar with Sohn et al. will ask what the BDD-specific addition is.
Our answer must be: the *unit of analysis* (scenario/step definition, not test method) and the
*drift between specification and behaviour*, not merely mutant survival.

**Bottom line to carry into the paper.** We may claim: *"No study has measured the oracle strength
of public BDD suites by mutation, nor tracked its evolution."* We may **not** claim: *"BDD quality
has not been studied"* (it has, extensively), *"BDD suites were never analysed at scale"* (they
were, statically), *"co-evolution of BDD specs and code was never measured"* (Zampetti 2020), or
*"longitudinal mutation analysis is new"* (Sohn et al. 2025). The defensible novelty is the
**intersection plus the domain-layer restriction**, and it is a narrow but real gap.

## Scope searched

Endpoints actually used (2026-11-25):
- **OpenAlex** `api.openalex.org` — primary discovery + abstracts (fast, stable on this host)
- **Crossref** `api.crossref.org` — DOI verification; heavily 429-throttled, so requests were
  paced 2–2.5 s apart with exponential backoff and retried 3–6×; results cached under `notes_db/`
- **Semantic Scholar** `api.semanticscholar.org` — abstract fallback (429-prone)
- **arXiv** PDFs and `arxiv.org/abs/` pages; **University of Bern SCG archive** (`scg.unibe.ch`) PDFs
- `web_search` / `web_fetch` tools
- **Blocked / unusable:** `dblp.org/search/publ/api` (non-JSON); `iris.unisannio.it` (Cloudflare 403);
  `core.ac.uk` (403); `link.springer.com` PDFs (403 to python urllib); ScienceDirect full text
  (paywall — Unpaywall reports `is_oa: false` for Zampetti 2020).

Query formulations (English and Portuguese): "Gherkin features open-source projects"; "BDD
scenarios quality evaluation"; "mutation testing Cucumber Gherkin scenarios fault detection";
"mutation analysis behavior-driven development test effectiveness"; "BDD smells / Gherkin
anti-patterns detection"; "step definitions reuse maintainability Cucumber"; "co-evolution test
code production code empirical"; "assertions in test code empirical study"; "vacuous tests never
fail assertion-free"; "test suite evolution mutation score longitudinal"; "controlled experiment
behavior-driven development effectiveness"; "behavior driven development empirical study
repository mining"; "evaluating effectiveness of BDD test suites"; "mutation testing acceptance
test suites industrial case study"; "test oracle automated acceptance testing"; "BDD specification
verification metrics"; "cucumber scenarios mutation score"; Portuguese: "qualidade de cenarios BDD
desenvolvimento guiado por comportamento".

## Papers opened

### zampetti2020demystifying — Demystifying the adoption of behavior-driven development in open source projects (Information and Software Technology 2020)
- **What it does:** three-phase empirical study of whether OSS projects use BDD frameworks, and
  whether BDD specifications co-evolve with source code.
- **Method / data:** (i) large-scale analysis of **50,000 popular open-source projects in five
  programming languages**; (ii) co-evolution of scenarios, fixtures and production code in a sample
  of **20 Ruby projects** via **Granger's causality test**; (iii) **survey of 31 developers**.
- **Key findings (verbatim numbers only):** "≃ 27% of the sampled projects use BDD frameworks";
  Ruby prevalence "68%"; "In about 37% of the cases, we found a co-evolution between
  scenarios/fixtures and production code."; "changes to scenarios and fixtures often happen
  together or after changes to source code"; survey respondents "write tests while/after coding
  rather than strictly applying BDD".
- **Their conclusion:** "Even if the BDD frameworks usage is widespread among open source
  projects, in many cases they are used for different purposes such as unit testing activities."
  (abstract truncated there; full text not retrievable).
- **What it does NOT answer for us:** no mutation analysis; no mutant kill share; no domain-layer
  isolation; no assertion measurement inside step definitions; no oracle-strength metric at all.
  Co-evolution is temporal precedence (Granger), **not** whether the suite would *catch* a
  behaviour change. 20 Ruby projects is a small longitudinal sample. Only the structured abstract
  could be read (publisher paywall, no OA copy), so nothing beyond it is quoted.
- **Threat it poses to our novelty:** **major** for the "drift exists" framing and for "Cucumber
  is often used as a unit-test framework" — that is *their* finding, we must attribute it;
  **minor** for mutation-based oracle strength, which they never touch.

### chandorkar2022gherkin — An Exploratory Study on the Usage of Gherkin Features in Open-Source Projects (SANER 2022)
- **What it does:** first empirical characterisation of how Gherkin syntax features (data tables,
  scenario outlines, backgrounds) are actually used in public spec files.
- **Method / data:** **1,572 spec files from 23 open-source projects**; per-file structural
  metrics; statistical comparison of specs with vs. without data tables.
- **Key findings:** "only a minority of the considered spec files (i.e., 590) used data tables
  that contain two rows, on average"; significant differences between the two populations,
  "especially for what concerns the number of lines of code (LoC)".
- **What it does NOT answer for us:** purely static/textual; nothing executed; step definitions not
  analysed; no assertions; no mutation; no history.
- **Threat:** minor. It proves the corpus type we want is extractable at scale (and that 23 repos
  is the scale the community has accepted so far).

### binamungu2018maintaining — Maintaining behaviour driven development specifications: Challenges and opportunities (SANER 2018)
- **What it does:** survey of BDD practitioners on BDD use, benefits, and maintenance challenges.
- **Method / data:** **75 BDD practitioners from 26 countries**.
- **Key findings:** "When the number of examples grows, BDD specifications can become costly to
  maintain and extend. Some teams find that parts of the system are effectively frozen due to the
  challenges of finding and modifying the examples associated with them."
- **What it does NOT answer for us:** perceptions only; no repository data; no measurement.
- **Threat:** minor — canonical citation for "BDD suites rot", which we cite and move past.

### binamungu2020characterising — Characterising the Quality of Behaviour Driven Development Specifications (LNBIP 2020)
- **What it does:** proposes four quality *principles* for BDD suites and collects practitioner
  opinion on them.
- **Method / data:** practitioner survey; principles proposed by the authors.
- **Key findings:** "Despite much discussion amongst practitioners and in the blogosphere, as yet
  no formal definition of what makes for a high quality BDD suite has been given."
- **What it does NOT answer for us:** quality defined by opinion, never by an execution-based or
  fault-detection criterion; explicitly no mutation.
- **Threat:** minor, and useful: it lets us contrast opinion-based quality criteria with an
  operational, mutation-based measure.

### binamungu2023mapping — Behaviour driven development: A systematic mapping study (JSS 2023)
- **What it does:** systematic map of all BDD research 2006–2021.
- **Method / data:** **166 papers**; RQs on venues, research types, topic evolution and
  *evaluation methods used in published BDD research*.
- **Key findings:** dominance of conference papers; scarcity of industry insight; "acute shortage
  of metrics for measuring various aspects of BDD specifications and the processes for producing
  BDD specifications".
- **Our own reproducible probe over the 65-page PDF:** `mutation`=0, `fault detect`=0,
  `step definition`=0, `smell`=0, `longitudinal`=0, `oracle`=1, `coverage`=2.
- **What it does NOT answer for us:** it maps the field; it measures nothing itself.
- **Threat:** none — our strongest single citation that mutation-based BDD suite evaluation is
  absent from the BDD literature.

### farooq2023bdd — Behavior Driven Development: A Systematic Literature Review (IEEE Access 2023)
- **What it does:** SLR synthesising BDD uses/applications and its impact on process and product
  quality.
- **Method / data:** SLR (abstract-level read; full text not fetched).
- **Key findings:** synthesises claimed BDD benefits; the abstract reports no suite-level
  fault-detection measurement.
- **What it does NOT answer for us:** no mutation, no oracle strength.
- **Threat:** none — a second, independent secondary study confirming the same vacuum.

### oliveira2019howtoevaluate — How to Evaluate BDD Scenarios' Quality? (SBES 2019)
- **What it does:** defines BDD scenario quality attributes and a question-based checklist.
- **Method / data:** interview-based study with **18 practitioners**; literature-informed initial
  set consolidated with practitioners' own criteria.
- **Key findings:** "there are only informal guidelines to guide practitioners on their BDD
  scenarios' elaboration and quality evaluations"; they "define a set of quality attributes and
  propose a question-based checklist".
- **What it does NOT answer for us:** the checklist is a human-judgement instrument; no execution;
  no mutation; **no correlation between checklist score and fault detection** — precisely the
  validation our design can add.
- **Threat:** minor (different instrument, no effectiveness measurement).

### oliveira2017empirical — On the Empirical Evaluation of BDD Scenarios Quality: Preliminary Findings of an Empirical Study (RE Workshops 2017)
- **What it does:** research-design paper asking whether known requirements-specification quality
  attributes (from use cases, user stories) transfer to BDD scenarios.
- **Method / data:** designed study run with **novice evaluators** (n NR in abstract).
- **Key findings:** "some of those attributes can be used to support BDD scenarios assessments".
- **What it does NOT answer for us:** preliminary, evaluator-perception based, no artefacts from
  repos, no execution.
- **Threat:** none — shows the research line's origin and that it stayed judgement-based.

### couto2023characterization — On the Characterization of Behavior-Driven Development Adoption Benefits: A Multiple Case Study (SBQS 2022)
- **What it does:** multiple case study characterising perceived BDD adoption benefits in teams
  novice to BDD.
- **Method / data:** multiple case study; student teams working with industry practitioners in
  active-based learning programmes.
- **Key findings:** "Perceived benefits are improved communication, faster delivery cycles, better
  product quality, among others."; "there is still no consolidated evidence about its benefits nor
  have we found quality indicators to measure them."
- **What it does NOT answer for us:** perceived benefits only; no test-suite artefact measurement.
- **Threat:** none; supports our motivation sentence.

### zhang2015assertions — Assertions are strongly correlated with test suite effectiveness (ESEC/FSE 2015)
- **What it does:** moves beyond test-suite size/coverage to *assertions inside test methods* as an
  effectiveness factor.
- **Method / data:** **6,700 composed test suites, 24,000 assertions, 5 real-world Java projects**;
  effectiveness measured by mutation.
- **Key findings:** "the number of assertions in a test suite strongly correlates with its
  effectiveness, and this factor directly influences the relation".
- **What it does NOT answer for us:** Java unit tests, not BDD; no step definitions; no history.
- **Threat:** **major for the mechanism, minor for the claim.** It is the paper that licenses our
  central hypothesis (fewer/weaker assertions in step definitions ⇒ weaker oracle). We must cite it
  as the theoretical basis, not pretend we discovered the mechanism.

### shrestha2011assertionsoracles — An Empirical Evaluation of Assertions as Oracles (ICST 2011)
- **What it does:** experiments with branch-adequate but **input-only (no-oracle)** suites vs
  runtime oracles vs embedded assertions, using muJava mutants.
- **Method / data:** **7 core Java classes + 2 sample programs**; synthetic faults from muJava.
- **Key findings:** oracles are "critical to the efficacy of the testing process"; suites that only
  exercise code detect little without an oracle.
- **What it does NOT answer for us:** no BDD, no step definitions, no repos, no history.
- **Threat:** minor for novelty; **major** as the precedent for our "vacuous/unassertive step"
  construct — the no-oracle condition is the lab version of a step definition with no assertion.

### zhi2013inadequateassertions — On Adequacy of Assertions in Automated Test Suites: An Empirical Investigation (ICSTW 2013)
- **What it does:** names and measures the **Inadequate-Assertion (IA)** problem in OSS test suites.
- **Method / data:** **3 active open-source projects**; **mutation analysis and coverage analysis**.
- **Key findings:** "test suites are prone to having inadequate assertions"; the paper reports IA
  occurrence via mutation and coverage analysis.
- **What it does NOT answer for us:** Java unit suites; no BDD; no longitudinal dimension.
- **Threat:** minor; it is the closest existing "mutation + weak assertions in OSS suites" study and
  the honest template we should say we extend to step definitions.

### kim2020testsmell — An empirical study on the evolution of test smell (ICSE-Companion 2020)
- **What it does:** studies how test smells evolve and why developers remove them.
- **Method / data:** repository mining over history (n NR in abstract).
- **Key findings:** "Assertion Roulette, Conditional Test Logic and Unknown tests have a high rate of
  churns, the feature addition and improvement motivate refactoring, but test smell persists,
  implicating sub-optimal practice."
- **What it does NOT answer for us:** no BDD, no Gherkin, no mutation effectiveness.
- **Threat:** minor; supplies the "quality erodes and stays eroded" longitudinal precedent.

### sun2023coevolution — Revisiting the Identification of the Co-evolution of Production and Test Code (TOSEM 2023)
- **What it does:** shows that the heuristics prior work used to mine production–test co-evolution
  samples are unreliable, and revisits their identification.
- **Method / data:** empirical re-analysis of mined co-evolution samples (n NR in abstract).
- **Key findings:** "Many software processes advocate that the test code should co-evolve with the
  production code"; the assumption that a test class changing together with (or shortly after) its
  production class constitutes a co-evolution sample is challenged.
- **What it does NOT answer for us:** nothing BDD-specific; no mutation.
- **Threat:** **methodological, and it must be answered in our design**: we cannot simply reuse
  commit-timestamp co-evolution heuristics; oracle strength must be measured directly.

### leotta2024mutta — Mutta: a novel tool for E2E web mutation testing (Software Quality Journal 2024)
- **What it does:** automates mutation testing of whole web applications against E2E suites, and
  uses it to compare two E2E styles.
- **Method / data:** **2 web applications; >15,000 mutants; ~87,000 test runs**; coverage-filtered
  mutants; comparison of (1) classical assertions vs (2) differential testing.
- **Key findings:** "Mutta has been executed on two web applications, each equipped with different
  test suites to compare assertions with differential testing"; the tool "can be successfully
  employed to automate the entire mutation testing process of E2E web test suites".
- **What it does NOT answer for us:** the suites are **not Gherkin/Cucumber-scoped**, mutants are
  server-source mutations (not domain-layer-restricted), only 2 applications, no history, and no
  BDD-only vs full-suite separation.
- **Threat:** **the most dangerous paper for our novelty** — it is the closest existing
  "mutation analysis of acceptance-style suites". Must be cited and differentiated explicitly
  (scale: 2 apps vs. our corpus; scope: E2E web vs. domain layer; no longitudinal component).

### irshad2022refactoring — Supporting refactoring of BDD specifications—An empirical study (IST 2022)
- **What it does:** action research to identify refactoring candidates in BDD specifications using
  two similarity measures, evaluated against an ML approach and manual identification.
- **Method / data:** **2 projects of a large software organisation** (Ericsson-scale), Action Research.
- **Key findings:** "Although refactoring is a crucial activity of BDD, little research is available
  on the topic"; refactoring candidates can be identified semi-automatically from similarity.
- **What it does NOT answer for us:** duplication/similarity is a *structural* proxy; nothing about
  whether the refactored suite still detects behaviour; industrial, not public repos.
- **Threat:** minor; but it is evidence that BDD duplication is an industrial concern, so our
  "drift" motivation should cite it.

### rwemalika2023suit — Smells in system user interactive tests (Empirical Software Engineering 2023)
- **What it does:** builds a catalogue of **35 SUIT-specific smells** and measures their diffusion
  and removal.
- **Method / data:** multi-vocal literature review + empirical analysis of **48 industrial repos and
  12 open-source projects**.
- **Key findings:** the same smell types appear in industrial and OSS projects "but they are not
  addressed in the same way"; smells spanning multiple code locations appear more often than
  single-line ones; "smell-removing actions are not frequent".
- **What it does NOT answer for us:** not Gherkin/BDD-scoped; no mutation; no oracle strength.
- **Threat:** minor; the best available citation that system-level test suites (the family BDD
  suites belong to) accumulate and rarely shed quality problems.

## Preprints consulted (read, but NOT in `refs/verified.bdd.csv`)

Protocol §1.2 requires a **Crossref-verified** DOI; arXiv DOIs are DataCite-registered, so a
Crossref lookup fails by construction. These two are recorded here for the Lead's decision and are
**excluded from the citation CSV**. Both matter to the novelty verdict, so they must not be lost.

### sohn2025latentmutants — Latent Mutants: A large-scale study on the Interplay between mutation testing and software evolution (arXiv:2501.01873, 2025; DOI 10.48550/arXiv.2501.01873)
- Applies mutation testing **in-time, across multiple project releases**; defines *latent mutants*
  (live in one version, killed in a later revision).
- Data: **131,308 mutants, Pitest, 13 open-source projects**; "Around 11.2% of these mutants are
  live, and 3.5% of them are latent, manifesting in 104 days on average"; predicts latent mutants
  with 86% accuracy / 67% balanced accuracy (random forest).
- **Why it matters:** it is the existing proof that longitudinal mutation analysis at scale is
  feasible and publishable — but on **Java unit suites**, not BDD, and with no domain-layer
  restriction. It is the paper a reviewer will name against our longitudinal claim.

### mughal2026dejavu — Deja Vu at Scale: Paraphrase-Robust Detection of Duplicate Gherkin Steps in Behaviour-Driven Software Testing with Sentence-Transformer Embeddings and a 1.1M-Step Open Benchmark (arXiv:2604.20462, 2026; DOI 10.48550/arXiv.2604.20462)
- Builds "the largest cross-organisational BDD step corpus to date": **347 public GitHub
  repositories, 23,667 `.feature` files, 1,113,616 Gherkin steps**, SPDX-tagged; plus a labelled
  pair-level benchmark (1,020 pairs, Fleiss kappa 0.84).
- Findings: "Step-weighted exact-duplicate rate is 80.2%; median-repository rate is 58.6%"; the top
  hybrid cluster has 20,737 occurrences across 2,245 files; estimates 893,357 corpus-wide eliminable
  step occurrences.
- **Why it matters:** it is the closest thing to "at scale on public BDD suites" — but it measures
  **step-text duplication**, not execution, not assertions, not mutants, and it has no temporal
  dimension. It also hands us a ready-made 347-repo corpus definition, which *helps* feasibility
  and slightly *weakens* the "at scale" adjective as a novelty claim. Cite it as the current
  frontier of BDD corpus work.

## Search log

| query | #hits screened | #opened | #kept |
| :--- | ---: | ---: | ---: |
| Gherkin features open-source projects | 10 | 2 | 1 (chandorkar2022gherkin) |
| BDD scenarios quality evaluation | 5 | 3 | 2 (oliveira2019howtoevaluate, oliveira2017empirical) |
| mutation testing Cucumber / Gherkin / acceptance tests | 25 | 3 | 1 (leotta2024mutta) |
| BDD smells / Gherkin anti-patterns | 10 | 2 | 1 (rwemalika2023suit) |
| step definitions reuse maintainability | 5 | 0 | 0 |
| co-evolution test code / production code | 5 | 3 | 1 (sun2023coevolution) |
| assertions in test code / oracles / vacuous tests | 10 | 3 | 3 (zhang2015, shrestha2011, zhi2013) |
| test suite evolution + mutation score (longitudinal) | 5 | 1 | 1 (sohn2025, preprint) |
| BDD systematic literature reviews / mapping studies | 10 | 2 | 2 (binamungu2023mapping, farooq2023bdd) |
| BDD effectiveness / controlled experiments | 10 | 2 | 2 (binamungu2018maintaining, couto2023characterization) |
| BDD specification refactoring / duplication | 10 | 2 | 2 (irshad2022refactoring, mughal2026, preprint) |
| Portuguese: qualidade de cenarios BDD | 5 | 0 | 0 |

## Coverage limitations (state these in the paper)

1. **Zampetti et al. 2020 full text was not obtainable.** No OA copy (Unpaywall `is_oa: false`),
   ScienceDirect paywalled, IRIS repository Cloudflare-403. Everything we say about it rests on its
   structured abstract, which is unusually detailed (it names all three phases, the sample sizes and
   the four headline numbers), but we cannot quote its RQ list or its threats-to-validity section.
2. **No IEEE Xplore / ACM DL full texts were read** except the ACM `fullHtml` variant that the search
   engine surfaced for Couto et al.; all other IEEE/ACM items are abstract-level
   (`crossref+abstract`), which the CSV records honestly.
3. **`dblp` search API is unusable on this host**, so venue-completeness cross-checking was done via
   OpenAlex only.
4. **Crossref throttling** (429) forced paced verification; 3 further DOIs
   (`10.1016/j.jss.2021.110944`, `10.1016/j.jss.2020.110840`) could not be verified in the time
   available and were therefore dropped rather than cited unverified.

## Dead ends

- **Portuguese-language literature:** OpenAlex returns only unindexed theses and non-peer-reviewed
  journal items ("UTILIZAÇÃO DA TÉCNICA DE BDD NO LEVANTAMENTO DE REQUISITOS", 2016; "Uma abordagem
  usando features BDD e modelo de objetivos", 2019; "An empirical study on the use of BDD and its
  support to requirements engineering", 2016). No peer-reviewed empirical scenario-quality study in
  Portuguese was found. Do not re-search.
- **`dblp.org/search/publ/api`** returns non-JSON from this host — use OpenAlex.
- **`iris.unisannio.it`** (Zampetti accepted MS), **`core.ac.uk`**, and **`link.springer.com`** PDFs
  are Cloudflare-403 to python urllib. Do not retry; use OpenAlex abstracts.
- **"Cucumber" as a query term** is polluted by plant biology (cucumber mosaic virus, sea cucumbers).
  Always qualify with BDD/Gherkin/testing.
- **Model-checking "BDD"** (binary decision diagrams) floods every query; always qualify with
  behaviour-driven/testing.
- **"How to Evaluate BDD Scenarios' Quality?"** exists twice in OpenAlex (ACM DOI + a Brazilian
  proceedings record with no DOI). Same paper; cite the ACM DOI only.
- **`UnifiedBDDLinter` (Zenodo, 2026)** and **"Empirical analysis of gherkin quality and common
  mistakes by novice testers" (E3S Web of Conferences, 2025)** surfaced but were rejected: Zenodo
  software records and a low-quality conference proceedings are not appropriate citations for the
  claim they would be used to support.
