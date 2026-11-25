# GATE 1.5 — Human review report

**Date:** 2026-11-25 (America/Sao_Paulo)
**From:** Lead Researcher / orchestrator
**To:** the human author
**Decision requested:** approve, revise, or reject entry into **P2** (full-corpus collection).
**Per the operating contract, no P2 collection has started and none will until you answer.**

---

## 0. Bottom line

The study is **buildable but not as specified**. Three things changed during P0–P1.5:

1. **Novelty survives, but only as a conjunction** — and one prior study (AAT4IRS 2024) has already
   used mutation analysis on a BDD acceptance suite. The claim must narrow.
2. **The venue is an Information Systems journal, not a software-engineering venue.** The paper as
   scoped risks desk rejection. This is the largest single risk to the deliverable and it needs a
   decision from you, not from me.
3. **The pilot yields 5.3 % eligibility, and the eligible set is the wrong shape** — dominated by
   BDD *tooling* repositories, skewed to Java, with **zero Python** and effectively zero TypeScript.
   The ≥20-scenario rule as written admits nearly the whole eligible set, but the domain-layer
   construct does not.

Everything below is backed by a file in this repository.

---

## 1. Novelty check (P0)

Full note: **`lit/novelty.md`**. 78 Crossref-verified works, all re-resolved by
`scripts/audit_refs.py` (78/78 PASS).

### Verdict: NOVELTY SURVIVES — for a narrower claim

The defensible claim:

> *No study has measured, on a corpus of public Cucumber-style suites, the mutation-based oracle
> strength of the BDD layer alone — separated from the contribution of the repository's other
> tests — nor how that strength changes across the repository's history.*

### The prior work that forces the narrowing

| Work | Why it matters |
|---|---|
| **dos Santos, Hallé, Petrillo, Guéhéneuc (2024)**, AAT4IRS, Frontiers in Robotics and AI, DOI `10.3389/frobt.2024.1346580` | **Already applied mutation testing to a BDD acceptance suite and reported 79 % of mutants detected.** One industrial pick-and-place proof-of-concept, hand-written mutant list, no public corpus, no BDD-vs-rest separation, no history. **Any claim that "mutation testing of BDD suites is new" is false.** |
| **Li, West, Escalona, Durelli (2015)**, ICSTW, DOI `10.1109/icstw.2015.7107453` | Closest *sounding* work. Verified twice, independently: the abstract says only "an industrial Ruby project", and the only openly available artefact — the Mutation-2015 slide deck — **never mentions Cucumber, Gherkin or BDD**. 1,716 mutants, MS 0.78 at 97.2 % statement coverage. It may **not** be described as scoring a Cucumber suite. |
| **Binamungu & Maro (2023)**, JSS, DOI `10.1016/j.jss.2023.111749` | Systematic map of **166 BDD papers (2006–2021)**. The string `mutat` appears **zero times**; it names an *"acute shortage of metrics for measuring various aspects of BDD specifications"*. This is our warrant. |
| **Leotta et al. (2024)**, Mutta, SQJ, DOI `10.1007/s11219-023-09616-6` | Mutation analysis of E2E web suites with coverage conditioning (>15 k mutants). Mutates servers, 2 apps, not Gherkin, no history. |
| **Zampetti et al. (2020)**, IST, DOI `10.1016/j.infsof.2020.106311` | BDD in OSS: 50,000 projects, ≈27 % BDD use, ≈37 % co-evolution, survey of 31 developers. No mutation, no kill share. **Full text unobtainable** (no OA copy; repository Cloudflare-403) — only its structured abstract is quoted, and the notes say so. |
| **Grano et al. (2021)**, TSE, DOI `10.1109/TSE.2019.2903057` | Static indicators estimate a *test case's* mutation score at 86 % F-measure. Closest threat to RQ3; different unit, no BDD, no longitudinal erosion. |

### Two construct findings you must see

- **`"specification drift"` is not an established SE term.** Crossref/OpenAlex return only 2025–26
  blog/arXiv/medRxiv usages. `"test decay"`, `"test erosion"`, `"test rot"` return **zero** SE papers
  for test suites. The paper must *coin and define* the term as a specialisation of **architectural
  drift** (Perry & Wolf 1992; Eick 2001; Izurieta & Bieman 2012) and hedge every use.
- **Van Deursen et al. (2001)** — origin of the test-smell catalogue — **has no DOI anywhere**
  (XP2001 workshop, CWI report SEN-R0119). The protocol forbids citing DOI-less work, so it is
  documented in `lit/notes.decay.md §DOI-less but essential` rather than cited. Its catalogue has
  **11** numbered smells, not the 12 usually quoted.

### Forbidden claims (now recorded in `lit/novelty.md §4`)
"BDD quality unstudied" · "BDD suites never analysed at scale" · "mutation testing never applied to a
BDD suite" · "longitudinal mutation is new" · "Li et al. measured a Cucumber suite" · "nobody related
static indicators to mutation score".

---

## 2. Venue rules — the scope problem (needs your decision)

Full record with URLs, dates and verbatim quotes: **`submission/VENUE-RULES.md`** (29 rules).

**iSys is the *Journal of Information Systems*** (SBC/CESI, Qualis A4). Its own guidance page says:

> *"A substantial number of submissions received by iSys … are returned during desk review due to
> misalignment with the Information Systems (IS) field. Many manuscripts treat information systems as
> a synonym for software systems, applications, or technical computing artifacts…"*
> — https://journals-sol.sbc.org.br/index.php/isys/understanding-is

> *"The field of Information Systems understands technology as a means rather than an end,
> emphasizing the phenomena that arise from its development, adoption, and use across organizational
> and social contexts."* — https://sol.sbc.org.br/journals/index.php/isys/about

Out-of-scope examples listed by the journal include *"Programming techniques or frameworks"*. A pure
mutation-testing-of-BDD-suites paper is, on that reading, **out of scope**, and desk review explicitly
checks scope alignment before external review.

**The escape route the journal itself provides:** technical artefacts *are* in scope when positioned
as **Design Science Research** — stating the organisational problem, the artefact's design rationale,
its evaluation in a relevant context, and implications for organisations. iSys also requires
*"proper coverage of SOL (SBC OpenLib) literature"* and names MISQ/ISR/EJIS/ICIS/SBSI as expected
reference venues.

**This is a positioning decision I should not make for you.** Three options:

| Option | What it costs | What it buys |
|---|---|---|
| **A. Reframe as IS/DSR** | ~1 new search facet (business–IT alignment, requirements traceability, IS quality, DSR), a rewritten introduction, a different reference base, and the paper becomes *"a validated instrument for detecting executable-specification drift in organisational information systems"*. Our `docs/PROTOCOL.md` artefact becomes the design-science contribution. | Scope alignment; a genuine IS contribution; uses the artefact the project already promised. |
| **B. Submit as-is to iSys** | High desk-rejection risk. | Nothing but speed. |
| **C. Change venue** | A different template, rules and review process; invalidates `VENUE-RULES.md`. | A better-fitting SE venue. |

**My recommendation: A.** It is also the only option under which the promised
`docs/PROTOCOL.md` deliverable is load-bearing rather than decorative.

---

## 3. Method (P1)

`docs/method.md` — 16-section pre-registration, ~7,100 words. Written before any collection; the
GitHub commit timestamp is the pre-registration evidence (OSF deposit is permitted by the venue and
still available to us: iSys states preprints are allowed on *"non-commercial repositories (e.g.,
arXiv, OSF)"*).

Highlights I verified myself rather than accepting:

- **Power analysis is arithmetically correct.** On the Fisher-z scale with
  `SE(z)=1.030/√(n−3)`: n=20→0.60, n=30→**0.50**, n=40→0.44; Holm α=0.025→**0.54**; per-stratum
  n=10→0.80. I recomputed all cells independently and they match. **The study can only detect
  |ρ| ≳ 0.5 at n=30** — this limit must appear in the paper.
- **Exactly two primary indicators** (`skip_ratio`, `assertion_weakness_ratio`) against one primary
  outcome (`MS_cov_bdd`), Holm-corrected; everything else is exploratory in one declared family.
- **No pooled Spearman as headline** — per-stratum ρ with bootstrap CIs, then a fixed-effects
  `stratum` model and a cluster bootstrap by stratum as the primary pooled CI.
- **BDD attribution has a mode-integrity assertion** (`executed(bdd) ⊆ executed(full)`, disjoint from
  non-BDD tests, count-equal to the dry run); a repo failing it is dropped, not patched.
- **ΔM_common** matches mutants across two snapshots by (file, operator class, original-line hash) and
  refuses to report if overlap < 50 % — so "erosion" is never inferred from incomparable mutant sets.

Nine `[GATE-DECISION]` items are consolidated in `docs/method.md Appendix A`; I concur with all nine
except that A9 (IS positioning) is §2 above and is yours to decide.

---

## 4. Tool feasibility — proven, not assumed

| Stratum | Result | Evidence |
|---|---|---|
| **JS/TS** | **FEASIBLE.** Stryker 10.1.1 + `@stryker-mutator/cucumber-runner` 10.1.1 drove a Cucumber 12.2.0 suite: **43 mutants, 31 killed, 72.09 %, 0 no-coverage**, with per-scenario test attribution. Ran twice, identical. | `results/RUNLOG.md` R001, `results/pilot/smoke-js-mutation.json` |
| **Java** | **FEASIBLE.** PIT 1.30.2 + `pitest-junit5-plugin` 1.2.3 + Cucumber-JVM 8.1.0 via the JUnit Platform engine: **19 mutants, 14 killed, 74 %, 0 no-coverage**, BUILD SUCCESS. Cucumber scenarios were discovered and named individually by PIT. | `results/RUNLOG.md` R002 |
| **Python** | **NOT ESTABLISHED / at risk.** PyPI resets connections (2–3 of 5 attempts succeed) and mutmut 3.x is coupled to pytest rather than accepting a BDD runner. Recorded as a stratum risk in R003, not silently dropped. | `results/RUNLOG.md` R003 |

Two environment facts that constrain the whole study and must be disclosed as limitations:

- **No Docker, no Maven, no Gradle on the host.** I vendored Maven 3.9.9 and Gradle 8.10.2 *inside
  the repository*, and only **JDK 22** is installed, so any corpus repository targeting Java 8/11/17
  may fail to build. There is **no build isolation** — cross-repo toolchain contamination is a real
  threat (method §14, T10) and is handled by per-repo cache localisation plus a repeatability probe.
- **Mutation tooling cannot run under the file sandbox.** Stryker died with `EPERM: spawn` under
  `workspace-write`; the recorded runs were executed unsandboxed. Any reproduction must run
  unsandboxed or in CI. This is stated in R001.

The Java probe also produced a **method-relevant number**: PIT reported 19 mutants for the same
domain logic where Stryker reported 43. That is direct local evidence for the literature's finding
that **tools are not on a common axis** (Kintis et al. 2018: equivalent mutants 203/94/382/43 across
four Java tools; *"no tool is able to subsume the others"*), and it is why the method forbids pooling
raw mutation scores across languages.

---

## 5. Pilot yield (P1.5) — the numbers

Frame: **2,552** unique repositories, enumerated token-free from 12 GitHub topic slugs × 5 language
filters × 6 pages = 252 pages, with a recorded snapshot hash
(`data/frame/FRAME.md`, SHA-256 `3b5e27f3…`). Sampling seed **20261125**, hash-ordered permutation
(`SHA-256("<seed>:<repo>")`), so the draw is reproducible in any language.

**Result over 170 screened repositories:**

| Funnel | n | share |
|---|---|---|
| **eligible after static screen** | **9** | **5.3 %** (95 % Wilson CI **2.8–9.8 %**) |
| too few scenarios (<20) | 76 | 44.7 % |
| no `.feature` files at all | 73 | 42.9 % |
| no step definitions | 6 | 3.5 % |
| licence not permissive / absent | 4 | 2.4 % |
| clone failed | 2 | 1.2 % |

**Extrapolated statically-eligible pool in the frame: 72–249 repositories.** Reaching the design
target n=30 needs roughly **570 screened repositories** (CI ≈ 306–1,071), i.e. about 22 % of the
frame — mechanically feasible (≈4 s/repo, so ≈40 min), but it must be approved and it must happen
*after* the frame is corrected (see next section).

A first pass on 45 repositories happened to yield **0** eligible; the 170-repository screen revised
that to 5.3 %. I report both because the discrepancy itself is informative: a 45-repo screen has a
wide interval and must not be used to conclude infeasibility.

### 5.1 The problem the eligible set reveals — this is the real gate issue

The 9 eligible repositories are:

| Repository | Lang | Features | Scenarios | Why it is or is not usable |
|---|---|---|---|---|
| `reqnroll/Reqnroll.VisualStudio` | C# | 50 | 997 | **Out of protocol strata** (.NET); .NET SDK broken on this host |
| `LeeShyanYeong/SpecWarden` | C#/TS | 4 | 64 | **Out of protocol strata** (.NET backend) |
| `Karzone/SpecReport` | C# | 11 | 38 | **Out of protocol strata** (.NET) |
| `reportportal/agent-java-cucumber6` | Java | 27 | 41 | BDD **reporting agent**, not an application with a domain layer |
| `reportportal/agent-java-cucumber` | Java | 22 | 34 | Same project family as above — **not independent** |
| `znsio/teswiz` | Java | 29 | 88 | BDD **test-automation framework**, not an application |
| `fslev/cucumber-jutils` | Java | 16 | 96 | BDD **utility library**, not an application |
| `trivago/cucable-plugin` | Java | 13→21 | 29 | Maven **plugin**, not an application |
| `Roopesh519/Cucumber-Assessment` | JS | 3 | 35 | An assessment exercise; no identifiable domain layer |

**Three consequences you need to weigh:**

1. **Language stratification as specified is not achievable from this frame.** Java 5 (+3 .NET, out
   of protocol), JavaScript 1, **TypeScript 0, Python 0**. The protocol's three-stratum design
   (Java / JS-TS / Python) is not present in the population the frame reaches. Either the frame
   changes, or the study becomes **single-language (Java)** — which is a legitimate design but a
   different paper, and it weakens the "at scale across ecosystems" framing that the novelty rests on.
2. **The frame is dominated by BDD *tooling and demo* repositories, not applications.** Our construct
   needs applications with an identifiable **domain layer**, because the entire "mutants as a proxy
   for business-rule change" argument depends on there being business rules. The eligibility rule as
   written (`*.feature` + steps + ≥20 scenarios + build + licence) does **not** test for that, and
   consequently admits reporting agents and utility libraries.
3. **The `>=20 scenarios` rule is not the binding constraint** — only 19 of 170 repositories reached
   20 scenarios, but most of those failed for other reasons. Relaxing it to ≥10 would add roughly 8
   candidates per 170 and would *not* fix the tooling-vs-application problem.

**My recommendation:** do **not** enter P2 with the current frame. Instead, spend one short phase
re-defining the frame to require, at frame-construction time, (a) a detected permissive licence and
(b) a detected application-shaped project (domain/source tree plus a test-scoped BDD dependency),
then re-run the seeded draw. This is a frame *definition* change, which is permitted **before** the
P1 gate closes, and it must be recorded in `docs/DEVIATIONS.md` and disclosed in the paper. It is not
free: it shrinks the frame and it changes what "the population" means.

---

## 6. Decisions I need from you

| # | Decision | My recommendation |
|---|---|---|
| **D1** | **IS positioning:** reframe as IS/Design-Science (option A), submit as-is (B), or change venue (C)? | **A** |
| **D2** | **Frame redefinition** to require licence + application shape at construction time, then re-draw? | **Yes** — the current frame cannot support the domain-layer construct |
| **D3** | **Language strata:** expand the frame for JS/TS + Python, or narrow the study to Java-only? | Expand first; fall back to Java-only if yield stays skewed after 300 screens |
| **D4** | **Bulk screening** of ~570 repositories (~40–90 min of clone+scan), after D2? | **Yes** |
| **D5** | **`docs/PROTOCOL.md` as DSR artefact** (the promised practical deliverable) — confirm it is in scope of the paper, not an afterthought? | **Yes**; it is the artefact that makes option A honest |
| **D6** | **Python stratum:** attempt a pinned `mutmut`/`cosmic-ray` install with retries, or drop Python and report it as a limitation? | Drop if two attempts fail; the brief explicitly allows dropping a stratum |
| **D7** | **OSF pre-registration** of `docs/method.md` now (venue permits it), or rely on the git commit timestamp alone? | **OSF** — it is free and it is the strongest anti-HARKing evidence |
| **D8** | **GitHub token.** None was supplied; the frame is therefore topic-based and cannot use code search. Provide a token? | Optional but valuable — it would let us verify the frame against code search |

---

## 7. What is already committed and verifiable

- `submission/VENUE-RULES.md` — 29 rules with URL, date and verbatim quote; 5 ambiguities disclosed.
- `refs/verified.csv` — 78 works, 78/78 Crossref-verified (`scripts/audit_refs.py` PASS).
- `lit/novelty.md` — gap statement, prior-work deltas, forbidden claims.
- `docs/method.md` — pre-registered protocol; power table verified independently.
- `results/RUNLOG.md` — R001 (JS) and R002 (Java) with command, UTC timestamp, git SHA, host, tool
  versions and artefact paths.
- `data/frame/` — frame enumeration with snapshot timestamp and HTML hash.
- `data/pilot/screen.csv`, `data/pilot/PILOT.md` — the full attrition dataset, every repo categorised.
- `pilot/smoke-js/`, `pilot/smoke-java/` — the working harnesses behind R001/R002.

Known gaps, stated rather than hidden: `lit/notes.bdd.md` and others contain `[CITE: …]` placeholders
S2 left for S1; `Martins et al. 2024 EMSE` (DOI `10.1007/s10664-024-10577-y`) is the one unresolved
novelty threat and must be read in full; Portuguese-language venues (SBES/CBSOFT) could not be swept
because DBLP is bot-blocked on this host.

---

## 8. Recommendation

**Do not enter P2 yet.** Close D1–D4 first: the venue positioning and the frame redefinition each
change what the study *is*, and both are cheap now and expensive later. The tooling risk that
normally kills BDD-mutation studies is settled — both Java and JS strata run end-to-end with
coverage-conditioned scores and per-scenario attribution.
