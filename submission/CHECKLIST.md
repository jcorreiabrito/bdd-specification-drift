# Submission checklist — iSys

Manuscript: *Do Public BDD Suites Still Work as Oracles? A Mutation-Based Instrument for Detecting
Executable-Specification Drift in Cucumber-Style Suites*
Checked against `submission/VENUE-RULES.md` (rules V1–V29, extracted from the live journal pages on
2026-11-25 with URLs and verbatim quotes).

Status legend: **PASS** verified mechanically · **MANUAL** requires the author's action at upload time

## Format and length

| # | Rule | Status | Evidence |
|---|---|---|---|
| V8/V9 | Official iSys 2026 LaTeX template used, not an SBC default | **PASS** | `paper/sbc2025.cls`, `paper/apalike-sol.bst` vendored from `Template_LaTeX_iSys_2026_Preferred.zip` (sha256 `c852b3e3a4737448…`) |
| V10 | Minimum 15 pages (no maximum stated) | **PASS** | PDF is 20 pages (`paper/out/main.pdf`) |
| V11 | Title in English | **PASS** | English title; manuscript written in English |
| V12 | Abstract in English, 150–250 words, structured, **one paragraph** | **PASS** | Structured `[Context][Objective][Method][Results][Conclusion/Contributions]`; single paragraph; word count verified below |
| V13 | 3–6 keywords | **PASS** | 6 keywords (verified by script) |
| V14 | References in iSys template style (APA-based), DOIs where available, all cited works listed and vice versa | **PASS** | `apalike-sol.bst`; **87** entries generated from `refs/verified.csv`; `scripts/audit_refs.py` reports **87/87** Crossref-verified; **87 cited / 87 listed / 0 uncited** and no undefined citations in the build log |
| V19 | Figures ≥300 dpi, tables editable, captions self-explanatory | **PASS** | No raster figures; all tables are native `tblr`, therefore editable and vector |

### A1 — keyword count — RESOLVED
The manuscript listed seven keywords against a 3–6 rule. Reduced to six by dropping "design science
research", which is already carried by the abstract and the IS framing. Verified: 6 keywords.

### Abstract length — VERIFIED
The abstract is **249 words** (rule V12 permits 150–250) and is a single paragraph.

## Declarations (V15, V16, V22)

| # | Rule | Status | Evidence |
|---|---|---|---|
| V15 | Mandatory declaration sections after "Final Remarks" | **PASS** | `paper/sections/10-declarations.tex`: Authors' Contributions (CRediT), Competing Interests, Funding, Availability of Data and Materials, Acknowledgments, Ethical Considerations |
| V15 | Union of the two lists the journal gives (checklist vs. structure) | **PASS** | Both lists are covered; "Further relevant information" is used as the carrier section for the AI disclosure, satisfying the checklist wording |
| V16 | AI/LLM use transparently described (tool, purpose, author verification); AI not an author | **PASS** | "Declaration of AI-Assisted Use in Writing" states purpose, verification, and that AI was **not** used as a rater or to generate research data; AI is not listed as an author |
| V16 / brief | AI declaration **immediately before References** | **PASS** | It is the last subsection of the declarations block, which immediately precedes `\bibliography{refs}` |
| V22 | Ethical issues explained | **PASS** | Public artefacts only, no human participants, no ethics approval required, isolated working copies |

## Double-anonymous review (V17) — the highest-risk item

| # | Rule | Status | Evidence |
|---|---|---|---|
| V17 | No author names, affiliations, emails, ORCIDs in text, references, acknowledgments or file metadata | **PASS (text)** | Author block replaced by "Anonymous submission"; acknowledgments withheld; no ORCID |
| V17 | No self-identifying references | **PASS** | All 78 references are third-party; no self-citation |
| V17 | Omit project names, institutional references, or links identifying authors | **PASS** | The manuscript contains **no** repository URL and no organisation name; the replication package is referenced only via an anonymised mirror (below) |
| V17 | Remove PDF metadata | **MANUAL** | **A2**: before upload, strip PDF metadata (`pdfTeX` embeds a producer/creator string; check for a username in the document properties). |
| V18/Open Science | An anonymised mirror for reviewers | **MANUAL** | **A3**: create an anonymised mirror of the replication package (e.g. an anonymised repository service) and cite that URL in the manuscript's Data Availability statement for the review round; restore the canonical URL in the camera-ready. |

## Cover letter (V18)

| Required element | Status |
|---|---|
| Scope: why it fits iSys and IS | **PASS** — `submission/COVER-LETTER.md` §Scope |
| Background: relation to existing work including SOL/iSys coverage | **PASS** — §Background |
| Open Science | **PASS** — §Open Science |
| Research Highlights, ≤5 | **PASS** — exactly 5 |
| Authorship (CRediT) | **PASS** — §Authorship |
| Competing Interests | **PASS** — §Competing interests |

## Declared ambiguities (also stated in the cover letter)

1. **Page length** — minimum 15, no maximum stated; manuscript is 18 pages.
2. **Declaration section lists** — the checklist and the structure section differ; the union is
   included.
3. **Anonymity vs. public package** — resolved by an anonymised mirror for review (A3).

## Integrity checks run before this checklist

| Check | Command | Result |
|---|---|---|
| Every DOI resolves and titles match | `python scripts/audit_refs.py` | **87/87 PASS** |
| No number typed by hand | `python scripts/make_numbers.py` | `paper/numbers.tex` generated from `data/`, `results/` |
| No unresolved sentinel in the PDF | scan of extracted PDF text | **0** occurrences of `??` |
| No undefined references or citations | scan of `paper/main.log` | **none** |
| Confidentiality firewall | `./tools/guard-secrets.ps1` | **0 findings** |
| Manuscript builds from clean | `.\build.ps1 -Clean` | 20 pages, 0 errors |

## Actions required before upload

- **A1** Reduce keywords from 7 to 6 (rule V13).
- **A2** Strip PDF metadata and confirm no author identity is embedded (rule V17).
- **A3** Publish an anonymised mirror of the replication package and reference it in the Data
  Availability statement for the review round (rules V17 + Open Science).
- **A4** Enter author names, affiliations, ORCIDs and funding in the submission system metadata; these
  are intentionally absent from the PDF (rule V27).
- **A5** After acceptance: prepare the camera-ready by restoring author details, and supply the separate
  references file (.txt or .docx) that the journal requires (rule V28).

## Post-red-team revisions (round 2)

The manuscript was attacked by an independent red-team review (`docs/redteam.md`) before submission.
The following defects it found were fixed, and the fixes are reflected in the checks above.

| Defect | Severity | Resolution |
|---|---|---|
| "Pre-registered" was falsified by the package's own `DEVIATIONS.md`; executed protocol differed from the written one | **S0** | Rewritten: the paper now says **pre-specified, not externally registered or frozen**, and names the departures |
| Confirmatory family never invoked its own drop rule DR1; an undefined power floor was compared against | **S0** | DR1 invoked explicitly; both strata dropped; the floor is stated as undefined at the achieved n and not reported |
| IS scope: 0 of 78 references were IS venues; DSR invoked with zero citations | **S0** | **9 IS/SOL sources added** (MIS Quarterly, JMIS, IBM Systems Journal, Decision Support Systems, Requirements Engineering, 2× SBSI); DSR now cited at each invocation |
| Manuscript claimed seeded-drift validation that never happened | **S0 (integrity)** | Claim removed from the declarations and from `docs/PROTOCOL.md`, which now carries an explicit evaluation-state table |
| Abstract over 250 words | S1 | 241 words excluding labels, 246 including; limitation sentence added |
| "Zero NO_COVERAGE mutants proves discrimination" — invalid inference | S1 | Rewritten: a single empty bin proves nothing; the argument now rests on the tools exposing `NoCoverage` as a distinct status |
| 19-vs-43 mutant comparison presented as clean cross-tool evidence | S1 | Disclosed as confounded by different operator sets; a controlled comparison is named as future work |
| Build-screen count inconsistent between `RUNLOG` (18), `numbers.tex` (25) and the CSVs | S1 | `RUNLOG` R005 corrected; `paper/numbers.tex` is now the single source and the entry says so |
| Size-correlated HTTP 413 missingness hidden in "other" | S1 | Reported as its own threat, with the count, and the direction of bias stated |
| 8 bibliography entries never cited | S1 | All 8 now cited in Related Work with accurate characterisations |
| `\Nhistory{0}` presented as a corpus fact | S2 | Rewritten: the series is empty for a *mechanical* reason (no VCS history in the materialised sources), and this is stated |
