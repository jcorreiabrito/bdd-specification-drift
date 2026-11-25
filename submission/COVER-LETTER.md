# Cover letter — submission to iSys

**Manuscript:** *Do Public BDD Suites Still Work as Oracles? A Mutation-Based Instrument for Detecting
Executable-Specification Drift in Cucumber-Style Suites*
**Type:** Research Article (full-length)
**Date:** 2026-11-25

> **Anonymity note.** This letter is written for the double-anonymous review process. Author names,
> affiliations and funding are withheld here and in the manuscript; they are supplied in the submission
> system and restored in the camera-ready version, as the journal's policy requires.

---

## Scope: why this fits iSys and the Information Systems field

The manuscript studies how an organisational rule survives its translation into an information
system. An information system, in the sense this journal uses the term, is a system of work in which
technology supports decision-making within organisational practice; its value comes from that
integration, not from technical functionality alone. Our subject is the artefact that is supposed to
hold that integration in place: the executable specification. In Behaviour-Driven Development (BDD),
business rules are written as Gherkin scenarios and executed as tests, on the premise that a change in
the implementation which contradicts the rule will fail the suite.

That premise can fail silently. A scenario can keep its business-facing text while its step
definitions stop checking anything, and then the artefact still *reads* as a specification while no
longer *functioning* as one. This is an organisational risk rather than a programming inconvenience:
the people who rely on the specification — auditors, product owners, compliance functions — are
precisely the people least able to see that its discriminating power has gone. We therefore treat the
problem as a design problem in the Information Systems sense and respond with a Design Science
artefact: a measurement protocol that makes the loss of discriminating power detectable.

The paper is grounded in IS concerns throughout, not only in its framing: the research questions
concern the reliability and validity of a measurement instrument for organisational artefacts
(RQ1), the contribution of a specification layer relative to the rest of an information system's
verification (RQ2), and whether the loss of that contribution accumulates over time (RQ3). The
discussion addresses implications for practice — what a steering committee should measure, and why
coverage is the wrong instrument — and for IS research.

## Background: relation to existing work, including iSys and SOL coverage

The work is positioned explicitly against four bodies of literature, all cited from
Crossref-verified sources: BDD adoption and scenario quality; mutation analysis as a measure of
discriminating power; the oracle problem and assertion quality; and the established literature on
decay and drift in architecture and code. Following the journal's guidance, we searched iSys and SOL
(SBC OpenLib) and the IS literature more broadly, and the manuscript cites the established drift
constructs on which our definition rests (architectural drift and erosion, code decay), together with
Brazilian-community work on BDD where it exists.

We are careful about what is new. A systematic mapping of 166 BDD papers found no treatment of
mutation analysis and named the shortage of specification-quality metrics as a gap. The closest prior
work applied mutation analysis to a BDD acceptance suite once, in a single industrial proof of concept.
Our claim is therefore narrow and stated as a conjunction: no study has measured, on a corpus of public
Cucumber-style suites, the oracle strength of the BDD layer *alone* — separated from the repository's
other tests — nor how it changes over history. The manuscript lists the claims we explicitly do *not*
make.

## Open Science: how data, code and materials are shared

A complete replication package accompanies the submission: the sampling frame with its snapshot hash
and sampling seed, the screening and attrition tables in which every candidate repository is recorded
in exactly one funnel state with a categorised reason, the static-indicator and mutation harnesses with
pinned tool versions, the raw per-mutant statuses, the analysis scripts, and an append-only run log
recording command, UTC timestamp, harness commit, host, seed and tool versions for every measurement.
No number in the manuscript is typed by hand: the file that supplies every quantitative value is
generated from those result files, and a missing source renders a visible sentinel rather than a
plausible-looking number.

Because review is double-anonymous, the package is made available to reviewers through an anonymised
mirror; the canonical public repository URL will be supplied in the camera-ready version. No
third-party source code or publisher PDF is redistributed.

## Research highlights (five contributions)

1. **A reusable instrument.** A five-step protocol that an organisation can apply to its own BDD suite,
   with coverage conditioning and differential attribution made mandatory rather than optional.
2. **Feasibility established, not assumed.** Mutation analysis driven by the BDD runner itself is
   demonstrated end to end in two ecosystems — PIT with the Cucumber-JVM JUnit-Platform engine, and
   Stryker with the official Cucumber runner — with per-mutant coverage status and per-scenario
   attribution, which is what the differential-kill construct requires.
3. **A pre-registered measurement of the population.** From a frame of 2,552 public repositories,
   94 (3.68 %) were statically eligible and, of the 18 build-tested, none produced a green, genuinely
   executing Gherkin baseline.
4. **A negative result with a mechanical explanation.** The binding constraint on evidence about BDD
   oracle quality is infrastructural rather than statistical: topic-tagged BDD repositories are
   overwhelmingly tooling, templates and demonstrations rather than applications with a domain layer
   and an executable specification.
5. **A quantified attrition analysis** that any future study of BDD effectiveness must confront, with
   the funnel published in full rather than summarised.

## Authorship (CRediT)

A single author contributed Conceptualization, Methodology, Software, Validation, Formal analysis,
Investigation, Data curation, Writing — original draft, Writing — review and editing, Visualization,
and Project administration. Names are withheld for double-anonymous review and supplied in the
submission system.

## Competing interests

The author declares no competing interests. No funding source supported this work or had any role in
its design, analysis, interpretation, or the decision to submit.

---

## Points the editors may wish to note (declared ambiguities)

The journal's guidance is clear on most points, but we flag three where we made a documented choice,
so that the choice is visible rather than buried:

1. **Page length.** The guidelines state a *minimum* of 15 pages and no maximum. The manuscript is
   18 pages. If the editors intend a maximum, we will adjust.
2. **Declaration sections.** The submission checklist and the structure section list slightly
   different sets of mandatory declaration subsections. We include the **union** of both, which
   satisfies either reading, with the AI-assisted-use declaration placed immediately before
   References.
3. **Anonymity versus a public replication package.** The guidelines ask authors to omit links that
   could identify them, while the Open Science policy asks for public data and code. We resolved this
   with an anonymised mirror for review and the canonical URL in the camera-ready version, as noted
   above.

We also wish to be explicit about one thing a reviewer will notice immediately: the study's empirical
contribution is a population and feasibility finding, not a measured correlation. We pre-registered a
correlation analysis, executed the instrument, and found that the public population does not supply
the units of analysis required. Rather than report an underpowered association as though it were a
result, the manuscript reports the funnel, the detectable-effect floor at the achieved sample, and the
instrument's validation on purpose-built harnesses. We believe a negative result of this kind is more
useful to the field than a fragile positive one, and we have written the paper so that a reader cannot
mistake which is which.

---

*Submitted for double-anonymous review.*
