# Human actions required before submission

Everything in this repository is either computed from logged runs or explicitly marked as
not done. This file lists the things **only a human can do**. Nothing here may be
substituted with a generated number, and several items are hard blockers for specific venues.

Status legend: **BLOCKER** (cannot submit without it) · **RECOMMENDED** (reviewers will ask)
· **OPTIONAL** (improves the paper, not required).

| # | Action | Owner | Status | Why it cannot be automated |
|---|---|---|---|---|
| H1 | Complete the two blinded coding sheets with **two independent raters**, then run `scripts/compute_irr.py` | Author + one colleague | **BLOCKER for any reliability claim** | Inter-rater reliability is by definition a property of two *independent humans*. A model coding both sheets measures self-consistency, not agreement. The study therefore reports no κ and says so. |
| H2 | Decide the venue and, if it is *iSys*, collect organisational/practitioner evidence (see below) | Author | **BLOCKER for iSys** | An IS journal expects evidence that the artefact matters to an organisation, not only that it computes. |
| H3 | Publish the replication package and replace the anonymised mirror link | Author | **BLOCKER before camera-ready** | Requires a public repository decision and a DOI (e.g. Zenodo) that does not exist yet. |
| H4 | Fill in the CRediT author allocation by name | Author | **BLOCKER before camera-ready** | Anonymity forbids it at review time; the journal requires it after acceptance. |
| H5 | Re-verify that no identifying metadata survives the final PDF build | Author | RECOMMENDED | Automated checks cover the current build; a human should open the PDF properties once. |
| H6 | Collect the full-history clones and re-run the longitudinal miner | Author with more time | RECOMMENDED | Needs network budget well beyond this session; the miner is implemented and unit-tested. |
| H7 | Provision a container runtime and re-run the build screen with pinned multi-runtime images | Author with infrastructure | RECOMMENDED | No Docker/Podman was available in this environment, so build screening ran on a single host and the resulting attribution is confounded (see Threats). |

---

## H2 in detail — what *iSys* expects, and what this paper currently has

**What the paper has.** A Design-Science-framed instrument, evaluated for (a) *feasibility* —
can mutation analysis be driven by the BDD runner at all, with a real `NO_COVERAGE` control
and a known-ground-truth validation campaign — and (b) *deployment conditions* — what a
census of the public population and a static indicator census say about whether the artefact
can be applied at scale. Both evaluations are complete and their numbers are traceable.

**What *iSys* would additionally expect.** The journal's scope is Information Systems, and
its reviewers typically ask for at least one of:

1. **A practitioner case**: the protocol applied inside one real organisation's BDD suite,
   with the indicator values, the mutation scores and the practitioner's decision recorded.
   Even a single case with a named role (anonymised) transforms the contribution from
   "the instrument computes" to "the instrument changed a decision".
2. **A walkthrough with a practitioner**: a structured session in which a developer or QA
   lead applies the protocol to their own repository while the researcher observes, with the
   friction points documented. This is cheaper than (1) and is the standard DSR
   "demonstration" evidence.
3. **A stakeholder evaluation**: interviews or a survey of practitioners who were shown the
   artefact and asked to judge its usefulness, relevance and usability, coded and reported
   with reliability.

**What would be sufficient for a Software Engineering venue instead.** *JBCS*, *JISA*,
*IST*, *EMSE* and similar venues accept the artefact's technical evaluation (feasibility +
known-ground-truth validation + public-population census) without an organisational case,
provided the threats to validity are explicit. This paper is currently at that level.

**Recommendation.** Submit as-is to a Software Engineering venue. For *iSys*, add one
practitioner walkthrough (option 2 above), which is the cheapest path to the organisational
evidence the journal expects, and state explicitly in the Discussion that the organisational
evaluation is a demonstration rather than a controlled study.
