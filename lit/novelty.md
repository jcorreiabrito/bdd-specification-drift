# Novelty note (P0 gate)

**Date:** 2026-11-25
**Author of this synthesis:** Lead Researcher, from four independent S1 search facets
(`lit/notes.bdd.md`, `lit/notes.mutation.md`, `lit/notes.decay.md`, `lit/notes.intersect.md`)
merged against `refs/verified.csv` (78 works, all Crossref-verified by `scripts/audit_refs.py`).

---

## 1. Decision

> **NOVELTY SURVIVES — but only for a narrower claim than the one in the project brief.**

The brief's claim, *"to our knowledge nobody has measured, with mutation analysis at scale, whether
public BDD suites still function as an oracle"*, is **too strong in one respect and correct in
another**. One prior study *has* applied mutation analysis to a BDD acceptance suite. Nobody has
done it at corpus scale on public repositories, nobody has separated the BDD layer's kill from the
rest of the suite, and nobody has measured its change over time.

## 2. What is already done (and therefore must NOT be claimed as new)

| Prior work | What it already establishes | Delta that remains |
|---|---|---|
| **dos Santos, Hallé, Petrillo, Guéhéneuc (2024)**, *AAT4IRS: automated acceptance testing for industrial robotic systems*, Frontiers in Robotics and AI, DOI `10.3389/frobt.2024.1346580` | A BDD **acceptance suite** evaluated **by mutation testing**; **79 % of generated mutants detected**. This is the single closest prior work and it invalidates any claim that "mutation testing of a BDD suite" is new. | One industrial pick-and-place proof-of-concept; **hand-selected domain mutants**; **no public corpus**; **no separation** of BDD-layer kill from other tests; **no temporal analysis**. |
| **Li, West, Escalona, Durelli (2015)**, *Mutation testing in practice using Ruby*, ICSTW, DOI `10.1109/icstw.2015.7107453` | Mutation testing inside an industrial Ruby project; 8 new Ruby operators; 1,716 mutants; MS 0.78 at 97.2 % statement coverage; practitioner lessons. | **Not a BDD study.** Verified independently by two agents: the abstract says only "an industrial Ruby project", and the only openly available artifact (the Mutation-2015 slide deck, `data/processed/pdf/…mutationTestingInPractice…txt`) **never mentions Cucumber, Gherkin or BDD**. It must not be described as scoring a Cucumber suite. |
| **Leotta et al. (2024)**, *Mutta*, Software Quality Journal, DOI `10.1007/s11219-023-09616-6` | Mutation analysis of **end-to-end web suites** (>15 k mutants, ~87 k E2E runs), **with coverage conditioning**. Nearest methodological neighbour. | Mutates **web servers**, not a domain layer; 2 applications; **not Gherkin**; no decomposition by test level; no history. |
| **Ojdanić et al. (FSE 2023)**; **Akour & Alenezi (2020)** | **Longitudinal mutation analysis** exists: 52 % of 143,500 mutants degrade across commits; mutation coverage tracked across 11 versions. | Not BDD; no drift indicators; no BDD-vs-rest decomposition. |
| **Niedermayr et al. (2016)** | Splits **unit vs system** suites under extreme (whole-method) mutation. | Precedent for *test-level decomposition in general*, **not** for a BDD/Gherkin layer specifically. |
| **Grano et al. (2021)**, TSE, DOI `10.1109/TSE.2019.2903057` | **Static indicators estimate a test case's mutation score** at 86 % F-measure. Closest threat to RQ3. | **Per test case**, for prioritisation; not suite-level drift indicators; not BDD; not longitudinal; no erosion construct. |
| **Binamungu & Maro (2023)**, JSS, DOI `10.1016/j.jss.2023.111749` | Systematic mapping of **166 BDD papers (2006–2021)**. | Its own finding is our warrant: the string `mutat` occurs **zero** times across the 65-page preprint, and it names an **"acute shortage of metrics for measuring various aspects of BDD specifications"**. |
| **Zampetti et al. (2020)**, IST, DOI `10.1016/j.infsof.2020.106311` | BDD in OSS at scale: 50,000 projects screened, BDD framework use ≈27 % (68 % in Ruby), co-evolution between scenarios and production code in ≈37 % of 20 Ruby projects (Granger causality), survey of 31 developers. | **No mutation, no kill share, no domain-layer isolation, no assertion analysis.** Full text was not obtainable (no OA copy; IRCd Cloudflare-403); only its unusually detailed structured abstract is quoted, and our notes say so. |
| **Kim et al. (2021)**, FSE, DOI `10.1145/3468264.3468609` | **3,111 disabling changes** in 122 K commits across 15 Java systems; **41 % of disabled tests never re-enabled**; median 39 days to re-enable, 92 days to delete. | Java unit tests; **disabling *flow***, not a **stock ratio**; nothing on Gherkin `@wip`/`@ignore`. |
| **Delplanque et al. (2019)**; **Feldt et al. (2014)** | "Rotten green tests" (294 found); test-case half-life 5–12 months. | Provide the **vocabulary** for assertion weakness and age; neither links to a mutation-based oracle measure. |

## 3. What remains genuinely unclaimed

> **No study has measured, on a corpus of public Cucumber-style suites, the mutation-based oracle
> strength of the BDD layer alone — separated from the contribution of the repository's other
> tests — nor how that strength changes across the repository's history.**

This is the defensible sentence. It contains four conjunctions, each of which is individually
unclaimed:

1. **Corpus scale on public repositories** — AAT4IRS is one industrial system.
2. **Domain-layer restriction** — Mutta mutates servers; AAT4IRS uses hand-selected mutants.
3. **Differential kill** (BDD-only vs full suite) — no precedent for any test-level decomposition
   in a BDD context; Niedermayr splits unit vs system, which is a different partition.
4. **Longitudinal erosion** — longitudinal mutation exists, longitudinal BDD co-evolution exists,
   but they have never been joined.

## 4. Claims that are now FORBIDDEN in the manuscript

- ✗ "BDD quality has not been studied." — It has, extensively (166-paper mapping study).
- ✗ "BDD suites have never been analysed at scale." — Chandorkar 2022; Mughal 2026 preprint (347 repos, 1.1 M steps); Zampetti 2020.
- ✗ "Mutation testing has never been applied to a BDD suite." — **AAT4IRS (2024) did exactly that.**
- ✗ "Longitudinal mutation analysis is new." — Ojdanić 2023; Akour & Alenezi 2020.
- ✗ "Li et al. (2015) measured a Cucumber suite." — **Not supported by any artifact we could open.**
- ✗ "Nobody related static test-quality indicators to mutation score." — Grano 2021 (per test case); Bhatta 2025 (deletion → mutation score); Martins 2024 proposes it explicitly.

## 5. Construct naming — a correction the paper must carry

`"specification drift"` is **not an established term in software engineering**. Crossref/OpenAlex
return only 2025–26 blog, arXiv and medRxiv usages; there is no peer-reviewed SE source that
establishes it. Likewise `"test decay"`, `"test erosion"` and `"test rot"` return **zero** SE papers
for test suites, and `"requirements drift"` is not established either.

Established relatives we must cite and build on instead:

- **architectural drift / erosion** — Perry & Wolf (1992), verbatim confirmed by our decay facet;
- **code decay** — Eick et al. (2001);
- **design-pattern decay / grime / rot** — Izurieta & Bieman (2012);
- **architectural drift** — Rosik et al. (2010);
- **test debt** — established (TestDCat 3.0, SQJ 2021).

**Recommendation:** define our construct explicitly as a *specialisation of architectural drift to
the executable-specification layer*, coin it in the paper with an explicit "we define" sentence, and
hedge every use. Do not write as though the term pre-exists. This must also appear as a limitation:
the construct's novelty is partly terminological, which is a weaker contribution than a new
empirical regularity and should not be oversold.

## 6. Residual risks to the novelty argument (disclose, do not hide)

1. **Two preprints were consulted but are excluded from `refs/verified.csv`** because the protocol
   requires a Crossref DOI: **Mughal 2026** (347 repos, 23,667 `.feature` files, 1,113,616 steps —
   weakens "at scale" as a novelty) and **Sohn 2025** (131,308 mutants across 13 Java projects —
   weakens "longitudinal mutation"). If they are published before submission they must be cited and
   the "at scale" phrasing dropped.
2. **Martins et al. (2024, EMSE, DOI `10.1007/s10664-024-10577-y`)** explicitly proposes combining
   test smells with mutation coverage. Only the ICSME'23 registered report was read. **This is the
   one unresolved threat to RQ3's novelty** and must be read in full before the paper is written.
3. **The BDD×mutation intersection was searched across four facets but with constrained access**:
   ACM DL, IEEE Xplore, Springer and ScienceDirect blocked most full texts. Portuguese-language
   venues (SBES, CBSOFT, SBC) could not be swept because DBLP is bot-blocked on this host. A
   librarian-assisted or on-campus pass is recommended before submission.
4. **Van Deursen et al. (2001)**, the origin of the test-smell catalogue, has **no DOI anywhere**
   (XP2001 workshop; CWI report SEN-R0119). The protocol requires a Crossref DOI for every
   citation, so it is documented in `lit/notes.decay.md §DOI-less but essential` rather than cited.
   The measured catalogue contains **11** numbered smells, not the 12 commonly quoted.

## 7. Consequence for the study design

The novelty now rests on **the conjunction**, so the design must not drop any conjunct:

- dropping the **differential kill** (RQ2) reduces us to AAT4IRS with more repositories;
- dropping the **longitudinal component** (RQ3) reduces us to Mutta with Gherkin;
- dropping the **domain-layer restriction** makes the "oracle strength" construct indefensible.

All three are load-bearing. If the pilot shows any one of them is unmeasurable, the honest response
is to narrow the paper's claim to what was actually measured — not to keep the claim and drop the
measurement.
