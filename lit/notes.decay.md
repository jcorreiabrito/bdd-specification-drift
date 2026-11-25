# decay — literature notes

Facet: **test decay, erosion, and disabled/skipped tests** (subagent S1-C). Host date 2026-11-25.
All rows referenced below have a Crossref-verified DOI and a row in `refs/verified.decay.csv`; the
comparison matrix is `lit/matrix.decay.csv` (27 rows). One foundational source (van Deursen et al.
2001) has **no DOI** and is therefore excluded from the CSV under protocol §1.2 — see
"DOI-less but essential" below.

---

## NOVELTY KILLED

**Not killed.** No paper in this facet measures the mutation-based oracle strength of public
BDD/Cucumber suites, and no paper computes longitudinal drift indicators over a suite's git history
and then regresses a *behavioural* oracle-strength measure (mutation score) on them.

But the novelty is **narrower than the project title implies**, and the Lead must not overclaim.
Three separate groups already own pieces of the longitudinal machinery:

1. **Git-mined dating of a test-level degradation event with exact lifetimes** — Kim et al. 2021
   (ESEC/FSE) already mined 122K commits, detected 3,111 disabling changes, and reported median
   re-enable (39 days) and delete (92 days) times plus a 41% never-re-enabled rate. Our
   skip/@wip-ratio indicator is a *transfer* of this design to Gherkin tags, not a new design.
2. **Survival analysis of test smells over commit history** — Cai et al. 2026 (PACMSE) and
   Feldt 2014 (ICST, test-case half-life 5–12 months) already establish the survival framing.
3. **Static indicators → mutation score** — Grano et al. 2021 (TSE) already predicts a test case's
   mutation score from source-code-quality indicators at 86% F-Measure/AUC-ROC, and Bhatta et al.
   2025 (MSR) already report that deleting 20% of redundant tests reduces coverage or mutation
   scores. Martins et al. 2024 (EMSE) explicitly set out to relate test-code quality and test smells
   to *code/mutation coverage*.

So the defensible gap is precisely: **suite-level, longitudinal, BDD-specific drift indicators
regressed on mutation-based oracle strength, with BDD-only kill separated from full-suite kill.**
Everything upstream of that sentence has precedent. See `## DESIGN IMPLICATIONS` (b).

---

## Scope searched

Databases / indexes hit: ACM DL (abstracts via Crossref JATS, conference program pages, and
web.archive.org replays), Springer (via web.archive.org only — direct `link.springer.com` is 403 on
this host), IEEE Xplore (via OpenAlex/Semantic Scholar abstracts and arXiv), Wiley (via
web.archive.org), arXiv, Crossref REST API (DOI verification), OpenAlex REST API (discovery +
abstracts), Semantic Scholar Graph API (abstracts, 429-prone), Unpaywall (OA check).
CWI institutional repository (`ir.cwi.nl`) for van Deursen et al. 2001.

Query families used (all run 2026-11-25):
`test smells empirical study prevalence evolution open source` · `disabled tests skipped tests empirical study open source prevalence` · `test decay test erosion software testing longitudinal` · `assertion weakening removal test code evolution study` · `flaky test quarantine empirical study` · `test debt technical debt in test code empirical` · `"test decay"` · `"test erosion"` · `"test rot"` · `"assertion weakening"` · `"rotten green tests"` · `"test quarantine" software` · `quarantine flaky tests developers practice` · `"disabled tests" empirical` · `"skipped tests" empirical` · `test suite evolution` · `co-evolution production code test code` · `"test smell" survival longitudinal` · `test smells mutation score` · `"specification drift" software` · `"requirement drift" software engineering` · `"architectural drift" definition empirical study` · `documentation drift empirical study software` · `Cucumber @wip @ignore tagged scenarios empirical study` · `RSpec pending xit skipped examples empirical study`

---

## Papers opened

### Kim2021Disabled — How disabled tests manifest in test maintainability challenges? (ESEC/FSE 2021)
- **What it does:** The first empirical study of the *practice of disabling tests* — prevalence of
  disabling changes, their life cycle, and the motivations behind them.
- **Method / data:** Tool mining **122K commits** across **15 open-source Java systems**, detecting
  four disabling forms: commented-out test code; commenting out or deleting `@Test`; JUnit
  `@Ignore`; TestNG `@Test(enable=false)`. Life-cycle analysis plus a manual study of **349 unique
  disabled tests** (95% confidence, 5% interval).
- **Key findings (verbatim numbers only):** **3,111 disabling changes** detected. "Test disabling
  changes are 19% more common than regular test refactorings, such as renames and type changes."
  "41% of disabled tests are never brought back to evaluate software quality, and most disabled
  tests stay disabled for several years." From Table 6 discussion: "the median time for developers
  to re-enable a test is 39 days"; deletion of a disabled test "median is 92 days".
- **What it does NOT answer for us:** Java/JUnit only — no Gherkin `@wip`/`@ignore`, no RSpec
  `xit`/`pending`. It never measures test *effectiveness*; the harm is argued as technical debt, not
  measured as lost mutant kill. No ratio-of-suite-at-a-point-in-time metric.
- **Threat it poses to our novelty:** **major** — for the skip-ratio indicator it is the direct
  precedent; we must cite it and frame our contribution as transfer + suite-level ratio
  operationalisation, not as a new construct.

### Feldt2014GrowOld — Do System Test Cases Grow Old? (ICST 2014)
- **What it does:** Introduces three concepts for aging in test-case use and failure behaviour:
  *test case activation curves*, *test case hazard curves*, and *test case half-life*.
- **Method / data:** Industrial system >1 MLOC; **1,620 system test cases**, "executed a total of
  more than half a million times over a time period of two and a half years".
- **Key findings (verbatim numbers only):** "system test cases stay active as they age but really do
  grow old; they go through an infant mortality phase with higher failure rates which then decline
  over time. The test case half-life is between 5 to 12 months for the two studied data sets."
- **What it does NOT answer for us:** Failure/activation only — nothing about assertions, skips,
  smells, or code churn. System tests, not unit or BDD. No mutation.
- **Threat it poses to our novelty:** **minor–major** — it owns the *survival* framing for test
  cases. Any "scenario half-life" or "hazard" claim must be positioned as an application of Feldt.

### Bhatta2025TestDeletion — Understanding Test Deletion in Java Applications (MSR 2025)
- **What it does:** Builds `DelTest`, a dataset of manually confirmed *deleted* tests, then studies
  deletion frequency, whether tests die with their class, and *why* they are deleted.
- **Method / data:** "449,592 commits from seven open-source Java projects"; **24,431** manually
  confirmed deleted tests.
- **Key findings (verbatim numbers only):** "83.2% of tests are deleted along with the corresponding
  test classes, while 16.8% are deleted individually." "91.4% of deleted tests in six projects are
  obsolete tests (i.e., production code is deleted), 7% are redundant tests (i.e., passing tests),
  and 1.6% are failing tests." "The deletion of 20% of redundant tests reduces code coverage or
  mutation scores." A TSR approach identifies "up to 54%" of redundant tests.
- **What it does NOT answer for us:** Deletion only (the terminal state), not disabling, weakening,
  or assertion changes. The mutation result is about redundant-test removal, not about a drift
  index, and is cross-sectional.
- **Threat it poses to our novelty:** **major for the gap question** — this is the closest existing
  link between a suite-erosion action and mutation score. Must be cited as nearest prior work.

### Pinto2012Myths — Understanding myths and realities of test-suite evolution (FSE 2012)
- **What it does:** First systematic study of how unit test suites evolve; introduces a technique
  and tool (TestEvol precursor) for classifying test-case changes.
- **Method / data:** "many versions of six real-world programs and their unit test suites".
- **Key findings (verbatim numbers only):** "test repair is just one possible reason for test-suite
  evolution, whereas most changes involve refactorings, deletions, and additions of test cases."
  (Secondary note, *not* a verbatim quote — Semantic Scholar TLDR: existing test-repair techniques
  that focus exclusively on assertions may have limited practical applicability.)
- **What it does NOT answer for us:** No effectiveness measure, no smells, no skip annotations, no
  BDD. Unit test suites of six programs.
- **Threat it poses to our novelty:** **minor** — it normalises "scenario removal/refactoring" as
  ordinary evolution, which *supports* our framing of drift as a natural process rather than as
  deviance.

### Cai2026PairedSmells — Paired Code Smells and Test Smells: A Fine-Grained Longitudinal Empirical Study (PACMSE 2026)
- **What it does:** Studies "paired smells" (a code smell and a test smell co-occurring in linked
  production and test code): association rules, survival lifespans, removal motivations.
- **Method / data:** "128,417 commits across 19 long-lived open-source Java repositories".
- **Key findings (verbatim numbers only):** "we identify 30 statistically significant rules where
  specific test smells imply the presence of underlying production code smells and our survival
  analysis reveals that in most repositories, paired smells have relatively shorter lifespans than
  unpaired ones."
- **What it does NOT answer for us:** Smells, not skips or assertions. No mutation. Not BDD. And
  crucially it measures smell *survival*, not oracle strength.
- **Threat it poses to our novelty:** **minor** — establishes that git-mined survival analysis of
  test smells is already published, so survival analysis per se is not our contribution.

### Kim2021SecretLife — The secret life of test smells — an empirical study on test smell evolution and maintenance (EMSE 2021)
- **What it does:** Evolution and removal mechanics of test smells, and whether smell metrics add
  explanatory power for post-release defects.
- **Method / data:** "12 real-world open-source systems"; longitudinal smell tracking; qualitative
  analysis of removals; statistical defect model.
- **Key findings (verbatim numbers only):** "1) Although the number of test smell instances
  increases, test smell density decreases as systems evolve. 2) … most test smell removal (83%) is a
  by-product of feature maintenance activities. 45% of the removed test smells relocate to other test
  cases due to refactoring, while developers deliberately address the only 17% … 3) Our statistical
  model shows that test smell metrics can provide additional explanatory power on post-release
  defects over traditional baseline metrics (an average of 8.25% increase in AUC)."
- **What it does NOT answer for us:** Defects, not mutation. No BDD. No skip/assertion signals.
- **Threat it poses to our novelty:** **minor**, but a *warnings* source: raw counts rise while
  density falls, so any count-based drift indicator must be normalised or it will report the wrong
  direction.

### Spadini2018Relation — On the Relation of Test Smells to Software Code Quality (ICSME 2018)
- **What it does:** Associates six test smells (and their co-occurrence) with change-proneness and
  defect-proneness of test code, and with defect-proneness of the tested production code.
- **Method / data:** "221 releases of ten software systems"; "more than a million test cases".
- **Key findings (verbatim numbers only):** "(i) tests with smells are more change-and defect-prone,
  (ii) 'Indirect Testing', 'Eager Test', and 'Assertion Roulette' are the most significant smells for
  change-proneness and, (iii) production code is more defect-prone when tested by smelly tests."
- **What it does NOT answer for us:** Outcome variables are change and defect proneness — **not**
  mutation score and **not** oracle strength. Release snapshots, not per-scenario git dating.
- **Threat it poses to our novelty:** **minor** — the closest *design* precedent (repeated
  snapshots + smells) but with a different outcome variable.

### Bavota2015AreTestSmells — Are test smells really harmful? An empirical study (EMSE 2015)
- **What it does:** Journal extension of Bavota et al. 2012: (1) prevalence of test smells in
  open-source and industrial systems; (2) controlled experiment on comprehension.
- **Method / data:** JUnit suites from open-source and industrial systems (system count NR in the
  abstract); controlled experiment with master students.
- **Key findings (verbatim numbers only):** "86 % of JUnit tests exhibiting at least one test smell
  and six tests having six distinct test smells"; "comprehension is 30 % better in the absence of
  test smells".
- **What it does NOT answer for us:** Comprehension, not oracle strength. No evolution over time in
  the journal version (single snapshot per system). No BDD.
- **Threat it poses to our novelty:** **minor** — but the 86% figure is the number reviewers will
  hold us to when we claim a prevalence of drift.

### Bavota2012Distribution — An empirical analysis of the distribution of unit test smells and their impact on software maintenance (ICSM 2012)
- **What it does:** Two studies: distribution of test smells in code; controlled experiment on
  whether smells affect comprehension during maintenance.
- **Method / data:** "18 software systems (two industrial and 16 open source)"; "a controlled
  experiment involving twenty master students".
- **Key findings (verbatim numbers only):** "test smells are widely spread throughout the software
  systems studied and … most of the test smells have a strong negative impact on the
  comprehensibility of test suites and production code."
- **What it does NOT answer for us:** Same as above; no time dimension, no effectiveness measure.
- **Threat it poses to our novelty:** **none–minor.**

### Martins2023Diffusion — On the diffusion of test smells and their relationship with test code quality of Java projects (JSEP 2023)
- **What it does:** Introduces the TSSM dataset and studies cross-project smell diffusion,
  co-occurrence, and correlation with structural metrics.
- **Method / data:** "13,703 open-source Java systems from GitHub"; `JNose Test` for smells, `CK`
  metrics for structure; projects split into three clusters.
- **Key findings (verbatim numbers only):** "The ratio of smelly test classes with a specific test
  smell is similar among the clusters, but we could observe a significant difference in the number
  of test smells among them."
- **What it does NOT answer for us:** Cross-sectional. No longitudinal component. No effectiveness.
- **Threat it poses to our novelty:** **none** for the core claim; **minor** as a scale benchmark
  (13,703 projects dwarfs any BDD corpus we can build, so we must not compete on scale).

### Spadini2020Severity — Investigating Severity Thresholds for Test Smells (MSR 2020)
- **What it does:** Elicits severity thresholds for four test smells and validates them with
  developers, arguing current detection rules are too strict.
- **Method / data:** "some 1,500 open-source projects" for threshold elicitation; developer study
  for validation.
- **Key findings (verbatim numbers only):** "current detection rules for certain test smells are
  considered as too strict by the developers"; the newly defined severity thresholds are "in line
  with the participants' perception".
- **What it does NOT answer for us:** No time dimension, no effectiveness, no BDD.
- **Threat it poses to our novelty:** **none** — but a methodological must-cite: an unthresholded
  smell count is not defensible.

### Panichella2022TwentyYears — Test smells 20 years later: detectability, validity, and reliability (EMSE 2022)
- **What it does:** Re-assesses whether the 20-year-old test-smell vocabulary matches real
  maintainability concerns, benchmarking two detectors against a hand-annotated dataset spanning
  developer-written and machine-generated suites.
- **Method / data:** "a hand-annotated dataset spanning hundreds of test suites both written by
  developers and generated by two test generation tools (EvoSuite and JTExpert)"; 6 smell types;
  multi-stage cross-validated manual analysis.
- **Key findings (verbatim numbers only):** "the current vocabulary of test smells is highly
  mismatched to real concerns: multiple smells were ubiquitous on developer-written tests but
  virtually never correlated with semantic or maintainability flaws"; "the older tool's detection
  strategies misclassified over 70% of test smells, both missing real instances (false negatives) and
  marking many smell-free tests as smelly (false positives)."
- **What it does NOT answer for us:** No longitudinal component; no mutation score; no BDD.
- **Threat it poses to our novelty:** **none directly**, but a **serious validity threat to any
  smell-based indicator** we plan. If a smell detector is wrong >70% of the time, smell counts cannot
  be load-bearing drift indicators.

### Pontillo2024ML — Machine learning-based test smell detection (EMSE 2024)
- **What it does:** Builds the largest manually validated test-smell dataset and tests whether ML
  beats heuristic detectors for four smells.
- **Method / data:** "the largest dataset of manually-validated test smells"; six machine learners;
  within- and cross-project settings.
- **Key findings (verbatim numbers only):** "The performance of the machine learning-based detector
  is significantly better than heuristic-based techniques, but none of the learners able to overcome
  an average F-Measure of 51%."
- **What it does NOT answer for us:** Detection only; no temporal or effectiveness analysis.
- **Threat it poses to our novelty:** **none**; reinforces the same validity caution as
  Panichella2022.

### Fushihara2023Trend — A Trend Analysis of Test Smells in Python Test Code Over Commit History (SEAA 2023)
- **What it does:** Analyses how test smells change across commit history, motivating better Python
  test-code management.
- **Method / data:** "100 open-source projects" (Python), commit-history analysis.
- **Key findings (verbatim numbers only):** "(1) a few kinds of test smells constitute the majority
  of smells detected in the studied projects, and (2) most kinds of smells tend to increase over
  commits, i.e., many test smells are likely to have remained in test code as technical debt."
- **What it does NOT answer for us:** Python unit tests, no BDD, no effectiveness measure, no
  skip/assertion signals.
- **Threat it poses to our novelty:** **minor** — direct precedent that "date the smell through git
  history" is an existing, published design.

### Athanasiou2014TestCodeQuality — Test Code Quality and Its Relation to Issue Handling Performance (TSE 2014)
- **What it does:** Builds a composite test-code-quality model (completeness, effectiveness,
  maintainability) from source metrics and correlates it with issue-handling performance.
- **Method / data:** Model applied to "18 open source systems"; issue repositories mined for defect
  resolution speed, throughput, productivity.
- **Key findings (verbatim numbers only):** "a significant positive correlation between test code
  quality and two out of the three issue handling metrics (throughput and productivity)".
- **What it does NOT answer for us:** "Effectiveness" in the model is metric-derived, **not**
  mutation score; outcome is issue handling.
- **Threat it poses to our novelty:** **minor** — evidence that the field's default outcome variable
  for test quality is maintenance performance, which is exactly what we intend to replace with
  mutation-based oracle strength.

### Delplanque2019RottenGreen — Rotten Green Tests (ICSE 2019)
- **What it does:** Defines and detects "rotten green tests" — tests that pass because some
  assertions never execute — via combined static + dynamic call-site analysis (tool `DrTest`).
- **Method / data:** "19,905 real test cases in mature projects of the Pharo ecosystem"; handles test
  helper methods, inherited helpers, trait composition.
- **Key findings (verbatim numbers only):** "it detected 294 tests as rotten-green tests that contain
  assertions that are not executed. Some rotten tests have been 'sleeping' in Pharo for at least 5
  years."
- **What it does NOT answer for us:** Pharo only; cross-sectional (no weakening history); no
  mutation score; not BDD.
- **Threat it poses to our novelty:** **major for the assertion-weakening indicator** — it owns the
  construct "a passing test that does not actually test". We must adopt its name and cite it.

### Aranega2021RottenGreen — Rotten green tests in Java, Pharo and Python: An empirical study (EMSE 2021)
- **What it does:** Cross-language replication of rotten-green-test detection, plus two new smells
  (`missed fail`, `missed skip`) arising from testing-framework misuse.
- **Method / data:** "approximately one hundred mature projects written in each of Java, Pharo, and
  Python".
- **Key findings (verbatim numbers only):** "they are also present in Java and Python projects, and
  that they fall into similar categories"; "we found code bugs that were hidden by rotten tests in
  Pharo and Python".
- **What it does NOT answer for us:** Still cross-sectional; no temporal weakening rate; no mutation
  score; no BDD.
- **Threat it poses to our novelty:** **major** — establishes that vacuous oracles are real and
  hide real bugs, and names `missed fail`/`missed skip`, which is very close to our "assertion
  weakening" and "skip" indicators coming from the other direction.

### Catolino2019AssertionDensity — How the Experience of Development Teams Relates to Assertion Density of Test Classes (ICSME 2019)
- **What it does:** Models the determinants of **assertion density** (assertions per test-class KLOC)
  and contrasts the model with a developer survey.
- **Method / data:** "12 software projects"; statistical model with team-experience factors;
  survey of "57 developers".
- **Key findings (verbatim numbers only):** assertion density is defined as "the number of assertions
  per test class KLOC, that has previously been shown as an effective way to decrease fault density";
  team experience is "a statistically significant factor in most of the systems".
- **What it does NOT answer for us:** No time dimension (no thinning rate), no mutation score, no BDD.
- **Threat it poses to our novelty:** **minor** — supplies a normalised assertion metric we can reuse;
  also proves normalised per-KLOC density metrics are accepted practice.

### Grano2021Lightweight — Lightweight Assessment of Test-Case Effectiveness Using Source-Code-Quality Indicators (TSE 2021)
- **What it does:** Tests whether production and test code-quality indicators can *estimate the
  mutation score* of a test case, avoiding expensive mutation analysis.
- **Method / data:** 67 candidate factors; a mutation-score estimation model; performance evaluation.
- **Key findings (verbatim numbers only):** "our estimation model only based on static features has
  86 percent of both F-Measure and AUC-ROC."
- **What it does NOT answer for us:** Individual test-case level; cross-sectional; indicators are
  code-quality factors, not drift indicators; no BDD; no time.
- **Threat it poses to our novelty:** **major for the gap question** — it is the closest existing
  work in the "static indicators → mutation score" direction, and it means our contribution cannot be
  "we are the first to link static indicators to mutation". Ours must be *suite-level, longitudinal,
  drift-specific, BDD-specific*.

### Martins2024TestRefactoring — Test code refactoring unveiled: where and how does it affect test code quality and effectiveness? (EMSE 2024)
- **What it does:** Registered report (ICSME 2023) → full EMSE 2024 paper. Investigates whether test
  refactoring targets test classes with quality/effectiveness concerns, and whether refactoring
  improves test-code quality and effectiveness.
- **Method / data:** Planned exploratory mining study of open-source Java projects combining "quality
  metrics, test smells, and code/mutation coverage indicators".
- **Key findings (verbatim numbers only):** quoted from the registered-report abstract (the EMSE full
  paper was not read): plan "to statistically analyze them in combination with quality metrics, test
  smells, and code/mutation coverage indicators … we will measure how refactoring operations impact
  the quality and effectiveness of test code."
- **What it does NOT answer for us:** *Not yet read in its published form.* It studies refactoring
  operations, not drift indicators, and not BDD.
- **Threat it poses to our novelty:** **must be resolved by the Lead** — this is the one paper in my
  facet that explicitly proposes to combine test smells with mutation coverage. The EMSE 2024 full
  text has to be read before the novelty claim is final.

### Zaidman2008CoEvolution — Mining Software Repositories to Study Co-Evolution of Production & Test Code (ICST 2008)
- **What it does:** Founding co-evolution study: do production code and tests change together?
- **Method / data:** "a project's versioning system, code coverage reports and size-metrics"; "two
  open source case studies"; results validated with log messages and the original developers.
- **Key findings (verbatim numbers only):** "we observe a number of different co-evolution scenarios."
- **What it does NOT answer for us:** No effectiveness measure, no drift indicators, no BDD, no
  survival analysis.
- **Threat it poses to our novelty:** **minor** — provides the vocabulary for pairing code churn with
  test churn (our "scenario age vs code churn" indicator borrows it).

### Marsavina2014CoEvolution — Studying Fine-Grained Co-evolution Patterns of Production and Test Code (SCAM 2014)
- **What it does:** Mines fine-grained changes and uses association rule mining to derive production↔
  test co-evolution patterns, then interprets them qualitatively.
- **Method / data:** "5 open-source systems"; association rule mining; qualitative interpretation.
- **Key findings (verbatim numbers only):** "The results show 6 co-evolution patterns and provide
  insights into their appearance along the history of the analyzed software systems."
- **What it does NOT answer for us:** No effectiveness; Java code, not Gherkin; no drift index.
- **Threat it poses to our novelty:** **minor** — methodological template for churn-pairing analysis.

### PerryWolf1992 — Foundations for the study of software architecture (ACM SIGSOFT SEN 1992)
- **What it does:** The conceptual foundation of software architecture (elements, form, rationale) and
  the origin of the **erosion / drift** pair in SE.
- **Method / data:** Conceptual.
- **Key findings (verbatim numbers only):** NR (conceptual paper, no quantitative result). The text
  (OCR-normalised, hence the PARAPHRASE marker in the CSV) attributes increasing brittleness to "two
  architectural problems: architectural erosion and architectural drift"; erosion "is due to
  violations of the architecture"; drift "is due to insensitivity about the architecture".
- **What it does NOT answer for us:** Architecture only; no tests, no measurement, no empirics.
- **Threat it poses to our novelty:** **none** — it is the vocabulary we inherit.

### Rosik2010ArchDrift — Assessing architectural drift in commercial software development: a case study (SPE 2010)
- **What it does:** Longitudinal in-vivo case study of architectural drift during de novo development,
  using Reflexion Modelling; checks whether detecting drift leads to its removal.
- **Method / data:** One commercial system; observation and think-aloud data.
- **Key findings (verbatim numbers only):** "implementations often diverge from their intended
  architectures: a phenomenon called architectural drift"; drift was detected but "detection of
  inconsistencies was insufficient to prompt their removal".
- **What it does NOT answer for us:** No tests, no quantification of drift magnitude, no BDD.
- **Threat it poses to our novelty:** **none** — but it gives the exact definitional move we need:
  drift = divergence between the intended artefact and the realised one. Our intended artefact is the
  Gherkin scenario layer; the realised one is the step-definition layer.

### Izurieta2012Decay — A multiple case study of design pattern decay, grime, and rot in evolving software systems (SQJ 2012)
- **What it does:** Defines and measures three graded degradation phenomena for design patterns:
  **decay**, **grime** (non-pattern code accumulating in pattern classes), and **rot** (breakage of
  structural/functional integrity).
- **Method / data:** "three successful object-oriented systems"; UML models generated from successive
  implementations; multiple case study.
- **Key findings (verbatim numbers only):** "We found no evidence of design pattern rot in these
  systems. However, we found considerable evidence of pattern decay due to grime"; "we found that the
  grime that builds up around design patterns is mostly due to increases in coupling."
- **What it does NOT answer for us:** Design patterns only; no tests.
- **Threat it poses to our novelty:** **none** — supplies the precedent that degradation is *graded*
  (decay vs grime vs rot), which is a good model for a drift taxonomy that is not binary.

### Wermelinger2011ArchEvolution — Assessing architectural evolution: a case study (EMSE 2011)
- **What it does:** Turns generic evolution laws and principles (Lehman's laws, Martin's design
  principles) into historical metrics and visualisations for architectural evolution.
- **Method / data:** Eclipse SDK; structural model with historical metrics.
- **Key findings (verbatim numbers only):** "while the Eclipse SDK does follow several of the laws and
  principles, there are some deviations" (no single effect size).
- **What it does NOT answer for us:** Architecture metrics, not tests; no effectiveness measure.
- **Threat it poses to our novelty:** **none** — it is the precedent for operationalising evolution
  laws as measurable indicators, which is exactly what a drift-index paper must do.

### Moonen2008Interplay — On the Interplay Between Software Testing and Evolution and its Effect on Program Comprehension (Springer 2008)
- **What it does:** Book chapter on the two-way interplay of testing and evolution; introduces
  "test-driven refactoring"; gives a research agenda.
- **Method / data:** Conceptual synthesis.
- **Key findings (verbatim numbers only):** NR. Key sentence: tests "can equally be experienced as a
  burden because they are subject to the very same forces of software evolution themselves."
- **What it does NOT answer for us:** Conceptual; no measurement, no empirics.
- **Threat it poses to our novelty:** **none** — it is the conceptual warrant for a *test-side* drift
  construct, and it is 18 years old, i.e. the warrant exists but was never operationalised for BDD.

---

## DESIGN IMPLICATIONS

### (a) Per-indicator verdict: precedent vs invention

| Planned indicator | Precedent in the literature | Verdict |
| :--- | :--- | :--- |
| **skip / @wip ratio** | **Kim2021Disabled** is the direct precedent: 3,111 disabling changes over 122K commits in 15 Java systems, median 39 days to re-enable, 92 to delete, 41% never re-enabled — for `@Ignore`, `@Test(enable=false)`, commented-out `@Test`, commented-out test code. **Feldt2014** is adjacent: a test that stops being executed is a test with zero activation, and activation curves are already a published construct. **Aranega2021** names `missed skip` as a smell. | **PRECEDENTED** for Java; **NOT precedented** for Gherkin `@wip`/`@ignore` or RSpec `xit`/`pending` — no empirical study of those exists (searched explicitly; only StackOverflow folklore). Our contribution is *transfer to the BDD layer* plus a **stock ratio** operationalisation (fraction of scenarios skipped at time *t*), which Kim et al. never compute — they count *flow* (disabling changes). That is an incremental, defensible extension, **not an invention**. Cite Kim2021Disabled as the anchor and say so in the paper. |
| **assertion weakening** | The *construct* is owned by **Delplanque2019** / **Aranega2021** under the name **"rotten green tests"** (assertions that never execute) plus the named smells `missed fail` and `missed skip`; 294 rotten tests in 19,905 Pharo test cases, some "sleeping" ≥5 years, and real bugs hidden by them. **Catolino2019** gives a cross-sectional normalised measure (**assertion density**, assertions per test-class KLOC). | **PARTIALLY PRECEDENTED, LONGITUDINAL FORM IS NEW.** The phrase "assertion weakening" returns **no** SE paper (OpenAlex/Crossref title+abstract search, 2026-11-25). Nothing measures the *rate at which assertions are weakened or removed over a suite's history*. Verdict: reuse their vocabulary ("rotten green test", "missed fail") and position our contribution as **diachronic** — the assertion-thinning *trajectory* — not as discovery of vacuous oracles. Do **not** claim the phenomenon is new; claim the *measurement over time* is. |
| **scenario age vs code churn** | Precedent exists in two halves that have never been joined for tests: (i) test-case aging and survival — **Feldt2014** (half-life 5–12 months, activation and hazard curves, 1,620 cases, >500K executions) and smell survival — **Cai2026** (128,417 commits, 19 repos); (ii) production↔test co-evolution churn — **Zaidman2008**, **Marsavina2014** (6 co-evolution patterns over 5 systems). | **METHODOLOGICALLY PRECEDENTED, APPLICATION NOVEL.** Nobody computes *per-scenario age* against *production-file churn*. Adopt Feldt's survival framing (activation / hazard / half-life) explicitly rather than inventing a new one — otherwise a reviewer will say we re-derived Feldt. |
| **duplicate scenarios** | **van Deursen et al. 2001, smell 11 "Test Code Duplication"** — verbatim from the CWI PDF: "Test code may contain undesirable duplication. In particular the parts that set up test fixtures are susceptible to this problem." Also **Bavota2012**/**Bavota2015** measure test-smell prevalence including duplication-lineage smells. | **PRECEDENTED at test-code level; invention at scenario-text level.** Duplication of *natural-language Gherkin scenarios* (semantically equivalent scenarios with different wording) has no study. Verdict: minor invention, well grounded; must cite van Deursen smell 11 and state that we extend duplication from code to specification text. |
| **scenario-to-step ratio** | **No precedent.** Nearest structural analogue is **Catolino2019**'s assertion density: "the number of assertions per test class KLOC" — the same logic of normalising a count of checking units by size. Nothing measures scenario-to-step-definition ratio. | **INVENTED METRIC with a precedented logic.** Verdict: defensible only if we explicitly justify it as the BDD analogue of assertion density, cite Catolino2019 for the logic, and validate it (e.g. show it correlates with something else) rather than assuming it means thinness. Without that, a reviewer will call it arbitrary. |
| **hardcoded values** | Canonical test smell: **Magic Number Test** — in the STEEL/JNose catalogue used by **Martins2023Diffusion** and **Pontillo2024ML**; **van Deursen et al. 2001** smells 10 "Sensitive Equality" and 1 "Mystery Guest" cover hardcoded literals and hidden fixtures. | **PRECEDENTED as a smell; not precedented as a drift indicator.** Nobody tracks hardcoded-literal *growth* over a suite's history. Verdict: minor invention; cite the Magic Number smell rather than coining a new name. |
| **"mirror" steps** | **No precedent under any name.** Nearest are **van Deursen et al. 2001** smell 8 "Indirect Testing" (a test class that tests something other than its counterpart), smell 9 "For Testers Only", and smell 5 "Eager Test"; plus "Assertion Roulette" (smell 7) for unreadable oracles. | **NOT PRECEDENTED — we would be coining.** Verdict: either define it operationally and validate it (e.g. show mirror steps increase with production-code coupling, cf. **Izurieta2012**'s grime-as-coupling finding), or drop it from the headline indicators and keep it as a qualitative taxonomy item. Do not present it as a recognised smell. |

**Cross-cutting verdict.** Four of the seven indicators (skip ratio, assertion weakening, duplicate
scenarios, hardcoded values) have named precedent and must be cited as such. Two (scenario age vs
churn, scenario-to-step ratio) are new *applications* of existing logics. One ("mirror" steps) is a
coinage. **And the whole smell-based family carries a heavy validity caveat**: Panichella2022 shows
that the smell vocabulary is "highly mismatched to real concerns" and that the older detector
"misclassified over 70% of test smells", while Pontillo2024 shows ML detectors plateau at
F-Measure 51%. Smell counts therefore cannot be load-bearing; the skip and assertion indicators,
which are syntactically verifiable, are much stronger.

### (b) Has anyone tied drift indicators to a *behavioural* effectiveness measure (mutation score)?

**No — the specific combination is open. But it is close, and three papers must be cited as nearest
prior work.**

The field's default outcome variable for test quality/degradation is **maintenance**, not mutation:

- **Spadini2018Relation** — outcome: **change-proneness and defect-proneness** of test code and of the
  tested production code (221 releases, 10 systems).
- **Bavota2015AreTestSmells / Bavota2012Distribution** — outcome: **comprehension** in a controlled
  experiment (30% better without smells).
- **Athanasiou2014TestCodeQuality** — outcome: **issue handling** (defect resolution speed, throughput,
  productivity) across 18 systems.
- **Kim2021SecretLife** — outcome: **post-release defects** (average 8.25% AUC increase).
- **Kim2021Disabled** — outcome: none behavioural; harm is argued as technical debt and life cycle.
- **Cai2026PairedSmells**, **Martins2023Diffusion**, **Spadini2020Severity**, **Panichella2022**,
  **Pontillo2024ML** — outcomes are smell existence, survival, severity, or detector accuracy. No
  behavioural oracle-strength measure.
- **Delplanque2019 / Aranega2021** — the only *behavioural* consequence anywhere in this set, and it
  is **real faults** ("we found code bugs that were hidden by rotten tests"), not mutation score.

Three near-misses that define the gap precisely:

1. **Bhatta2025TestDeletion (MSR 2025)** — "The deletion of 20% of redundant tests reduces code
   coverage or mutation scores." This is a **suite-erosion action → mutation score** link, but
   cross-sectional, about *redundant* test removal, and not driven by a drift index.
2. **Grano2021Lightweight (TSE 2021)** — a static-indicator model estimates a **test case's mutation
   score** at 86% F-Measure and AUC-ROC. This is the closest thing to "indicators → mutation", but it
   is **individual-test-case, cross-sectional, and generic quality factors**, not suite-level drift
   indicators over time.
3. **Martins2024TestRefactoring (EMSE 2024, registered report ICSME 2023)** — explicitly proposes to
   combine "quality metrics, test smells, and code/mutation coverage indicators" to measure how
   refactoring affects test effectiveness. **This is the one paper that could erase part of our
   contribution and its published version has not been read. Flagged for the Lead.**

**Consequence for our claim.** We must not write "no one has related test-quality indicators to
mutation score". We must write the narrower, true sentence: *no study computes longitudinal
suite-level drift indicators for BDD/Cucumber specifications and regresses a mutation-based oracle
strength measure on them, separating BDD-only from full-suite kill*. That sentence survives all 27
papers I opened.

### (c) Is "specification drift" an established SE term?

**No — we would be coining it.** And "requirements drift" is not established either.

Evidence (searches run 2026-11-25, Crossref + OpenAlex title/abstract + web):
- `"specification drift" software` returns **only** 2025–2026 material: an LLM-agent Zenodo preprint,
  a medRxiv clinical-scoring paper, SSRN/arXiv preprints on agentic coding, and industry blogs
  ("spec drift"). **No peer-reviewed SE paper defines or uses it as a construct.**
- `"requirement drift" software engineering` returns glossaries and unrelated hits — no SE paper.
- `"test decay"`, `"test erosion"`, `"test rot"` return **zero** software-engineering papers; every
  hit is civil/astrophysical/agronomic ("Jet Erosion Test", "testing decay resistance of lumber").
  These terms are **not** part of the SE vocabulary for test suites.

What *is* established, and who established it:

| Term | Established by | Meaning |
| :--- | :--- | :--- |
| **architectural erosion** | **Perry & Wolf 1992** (SEN 17(4)); surveyed later by de Silva & Balasubramaniam (JSS 2012, paywalled — see Dead ends) | violations of the intended architecture |
| **architectural drift** | **Perry & Wolf 1992**; operationalised by **Rosik2010** ("implementations often diverge from their intended architectures: a phenomenon called architectural drift") | insensitivity about the architecture; divergence of implemented from intended architecture |
| **code decay** | Eick et al. 2001 (TSE) — *paywalled, could not open; excluded from the CSV* | files become harder/riskier to change over time |
| **design pattern decay / grime / rot** | **Izurieta2012** | graded degradation of pattern realisations; grime driven mostly by coupling |
| **architectural evolution vs Lehman's laws** | **Wermelinger2011** | historical metrics assessing a system against evolution laws |
| **test code / specification-level drift** | *nobody* | — |
| **test debt** | TestDCat 3.0 (SQJ 2021) and "Understanding Test Debt" (2016) — *identified but abstracts not retrieved* | debt metaphor applied to test artefacts |

**Recommendation.** Keep "specification drift" as *our* term, but do three things: (i) define it in
one sentence as a specialisation of architectural drift to the **executable-specification layer**
(intended = Gherkin scenarios; realised = step definitions / production behaviour), citing
**PerryWolf1992**, **Rosik2010** and **Izurieta2012**; (ii) add explicit hedging ("we are not aware of
prior use of *specification drift* for executable specifications"); (iii) consider the unambiguous
alternative **"executable-specification drift"** or **"scenario drift"** in the title, so no reviewer
thinks we are borrowing a standard term we are not. Do **not** lean on "test decay"/"test erosion" as
if they were established — they are blog vocabulary, not SE vocabulary.

---

## Search log

| Query | Hits screened | Opened | Kept |
| :--- | ---: | ---: | ---: |
| `test smells empirical study prevalence evolution open source` | 10 | 6 | 5 |
| `disabled tests skipped tests empirical study open source prevalence` | 10 | 4 | 1 |
| `test decay test erosion software testing longitudinal` | 10 | 2 | 0 |
| `"test decay"` (OpenAlex) | 8 | 0 | 0 |
| `"test erosion"` (OpenAlex) | 8 | 0 | 0 |
| `"test rot"` (OpenAlex) | 8 | 0 | 0 |
| `"assertion weakening"` (OpenAlex) | 8 | 0 | 0 |
| `"rotten green tests"` (OpenAlex) | 8 | 4 | 3 |
| `"disabled tests" empirical` (OpenAlex) | 8 | 1 | 1 |
| `"skipped tests" empirical` (OpenAlex) | 8 | 2 | 1 |
| `"test suite evolution"` (OpenAlex) | 8 | 3 | 2 |
| `co-evolution production code test code` (OpenAlex) | 8 | 3 | 2 |
| `"test smell" survival longitudinal` (OpenAlex) | 8 | 3 | 3 |
| `"test debt"` (OpenAlex) | 8 | 2 | 0 (abstracts unobtainable) |
| `test smells mutation score` (OpenAlex) | 6 | 2 | 2 |
| `assertion weakening removal test code evolution study` | 10 | 2 | 1 |
| `flaky test quarantine empirical study` | 10 | 3 | 0 (out of scope) |
| `test debt technical debt in test code empirical` | 10 | 2 | 0 |
| `"specification drift" software` (OpenAlex) | 8 | 0 | 0 |
| `"requirement drift" software engineering` | 10 | 0 | 0 |
| `"architectural drift" definition empirical study` | 10 | 3 | 3 |
| `documentation drift empirical study software` | 10 | 2 | 0 (drift of prose docs, not specs) |
| `Cucumber @wip @ignore tagged scenarios empirical study` | 10 | 0 | 0 (no scholarly hits) |
| `RSpec pending xit skipped examples empirical study` | 10 | 0 | 0 (no scholarly hits) |
| Crossref `query.bibliographic` exact-title lookups | ~60 | ~45 | 27 |
| OpenAlex DOI lookups (abstract retrieval) | 30 | 30 | 24 |
| Wayback replays of Springer/Wiley abstract pages | 6 | 6 | 4 |

Totals: **27 papers opened and kept**, each with a Crossref-verified DOI.

---

## DOI-less but essential (excluded from the CSV, needs a Lead decision)

**van Deursen, A.; Moonen, L.; van den Bergh, A.; Kok, G. — "Refactoring test code" (XP2001).**
- Verified by opening the open-access CWI report: `https://ir.cwi.nl/pub/4324/04324D.pdf`
  (report **SEN-R0119**, ISSN 1386-369X, 31 July 2001, 8 pages).
- **No DOI exists** for this paper: Crossref `query.bibliographic` returns only unrelated works, and
  the XP2001 workshop proceedings were never DOI-registered. Protocol §1.2 therefore forbids citing
  it. **Lead must decide** whether to (i) cite it as a DOI-less technical report with an explicit
  exception note in the paper, or (ii) cite a DOI-bearing source that reproduces the catalogue
  (e.g. Bavota2012 / Spadini2018 / Panichella2022, all of which cite it).
- **The catalogue, verbatim from the PDF — I count 11 numbered smells, not the 12 often quoted**
  (Gerard Meszaros's page says 12; the CWI PDF has 11 numbered headings):
  1 Mystery Guest · 2 Resource Optimism · 3 Test Run War · 4 General Fixture · 5 Eager Test ·
  6 Lazy Test · 7 Assertion Roulette · 8 Indirect Testing · 9 For Testers Only · 10 Sensitive
  Equality · 11 Test Code Duplication.
- Verbatim definition of smell 7: "This smell comes from having a number of assertions in a test
  method that have no explanation. If one of the assertions fails, you do not know which one it is."
- Verbatim definition of smell 11: "Test code may contain undesirable duplication. In particular the
  parts that set up test fixtures are susceptible to this problem."
- **This is the single most important citation in my facet and it is the only casualty of the DOI
  rule.** Please resolve it explicitly in the paper's method or threats section.

---

## Dead ends (do not re-search)

- **"Test decay", "test erosion", "test rot"** — no SE literature exists. All hits are other
  disciplines. If we use these words we are coining; prefer "erosion"/"drift" with explicit citation.
- **Eick, S.; Graves, T.; Karr, A.; Marron, J.; Mockus, A. — "Does code decay? Assessing the evidence
  from change management data" (TSE 2001), DOI 10.1109/32.895984.** Crossref-verified metadata, but
  **not open access** (Unpaywall `is_oa: false`, no repository copy, the NTNU PDF is a dead link,
  CiteSeerX returns 404). Could not read an abstract or body → **excluded from the CSV** under
  protocol §1.1. If the Lead can obtain it, it is the canonical source for "code decay".
- **de Silva, L.; Balasubramaniam, D. — "Controlling software architecture erosion: a survey" (JSS
  2012), DOI 10.1016/j.jss.2011.07.036.** Crossref-verified, **not open access**, ScienceDirect page
  was not replayable in the Wayback Machine → excluded. Useful only if we want a survey citation for
  erosion; **PerryWolf1992** covers the definition.
- **Peruma, A. et al. — "On the distribution of test smells in open source Android applications"
  (CASCON 2019).** No Crossref DOI found for the CASCON proceedings paper → excluded. Android-only,
  marginal for us.
- **Test flakiness / quarantine literature** (e.g. flaky-test surveys at ICST 2022, flaky tests in
  Python/JavaScript, "Predicting the Lifetime of Flaky Tests on Chrome" FTW 2024). Deliberately
  **out of scope**: flakiness is *nondeterminism*, not decay, and quarantine lifetime is not
  skip-annotation lifetime. Relevant only as a contrast: quarantine is an *explicit, time-boxed,
  tracked* response to flakiness, whereas `@Ignore`/`@wip` is untracked. That contrast is a good
  motivation sentence, not a citation base.
- **"TestDCat 3.0" (SQJ 2021, 10.1007/s11219-020-09533-y)** and **"Understanding Test Debt" (2016,
  10.1007/978-981-10-1415-4_1)** — identified as the canonical sources for the term **test debt**, but
  their abstracts could not be retrieved (Springer 403, no Wayback snapshot, no OA copy). **Unverified
  leads**; do not cite without opening.
- **Diaz Pace, J. A. et al. — model-code / design-code drift ("ArchSync")** — surfaced in search as
  the closest thing to "specification drift" for models vs code. **No DOI verified, not opened.**
  Worth one lookup if the Lead wants to strengthen the drift-vocabulary section.
- **"Test Weakening: Measuring Repair without Eroding Tests" (Zenodo, 2026)** — LLM-agent artifact
  about agents weakening assertions to make CI pass. **Not a peer-reviewed SE paper**, not about human
  suites, and its numbers do not transfer. Ignored.
- **"Copy, Paste, Fail: Measuring the Reliability of Executable Documentation" (IEEE, 2026)** —
  documentation drift on READMEs. Superficially attractive for "executable documentation" but it is
  about install instructions, not specifications; not opened.

---

## Honesty about coverage (protocol §5)

1. **Almost all quantitative findings above come from abstracts, not full texts.** Paywalls blocked
   the body text of Spadini2018, Bavota2015, Bavota2012, Kim2021SecretLife, Martins2023,
   Martins2024, Athanasiou2014, Pinto2012, Bhatta2025, Cai2026, Catolino2019, Marsavina2014,
   Zaidman2008, Delplanque2019, Aranega2021, Grano2021, Panichella2022. Only **Kim2021Disabled**,
   **Feldt2014** (arXiv), **PerryWolf1992** and **van Deursen 2001** were read as full PDFs. Where the
   abstract gave no number I wrote `NR` rather than estimating.
2. **`dl.acm.org` returns HTTP 403 to this host**, so ACM body text and ACM abstract pages were
   unreachable; ACM abstracts were recovered through Crossref JATS deposits, OpenAlex and Semantic
   Scholar instead. `link.springer.com` redirects to `idp.springer.com`; Springer abstracts were
   recovered through `web.archive.org` replays of the article pages.
3. **The EMSE 2024 full version of Martins2024TestRefactoring was not read** — only the ICSME 2023
   registered report. This is the one unresolved threat to the novelty claim and is flagged above.
4. **No empirical study of Gherkin `@wip`/`@ignore` or RSpec `xit`/`pending` could be found at all.**
   This is a genuine gap in the literature, not a search failure: I searched acronym-level and
   framework-level terms and got only StackOverflow/RSpec-docs hits. It is a small, publishable
   descriptive contribution on its own, and it makes our skip-ratio indicator the first of its kind
   for BDD suites.
5. **Two seam areas were not searched at all** because they sit outside my facet: BDD/Gherkin quality
   per se (other agents), and mutation testing of BDD suites (other agents). If someone has already
   run mutation analysis on Cucumber suites, my gap statement is moot and their findings must be
   merged.
6. **All 27 DOIs in `refs/verified.decay.csv` were re-resolved against `api.crossref.org` in a final
   sweep: 27/27 resolved, 0 failures.** One known year discrepancy for the Lead's merge script:
   `Bavota2015AreTestSmells` is recorded as **2015** (EMSE vol. 20 no. 4, August 2015, pp. 1052–1094 —
   the version of record) while Crossref's `issued` field says **2014-05-31** (online-first). Same for
   `Grano2021Lightweight` (recorded 2021 = TSE issue date; Crossref `issued` 2021-04-01, early access
   2019). If the merge script cross-checks years against Crossref, expect these two to flag.
7. **`Cai2026PairedSmells` has a single author in Crossref (`Cai, Z.`)** for a 2026 PACMSE paper. That
   is unusual for a 128K-commit study and may be an incomplete Crossref deposit. **Verify the author
   list against the PDF before the bibliography is finalised.**
