# VENUE-RULES.md — iSys (Revista Brasileira de Sistemas de Informação / Journal of Information Systems)

**Rule-extraction date:** 2026-11-25 (America/Sao_Paulo)
**Extracted by:** Lead Researcher, from live journal pages (no assumptions from SBC defaults).
**Evidence:** every page quoted below is cached verbatim under `data/raw/` with SHA-256 and UTC
retrieval timestamp in `data/raw/INDEX.jsonl`; readable text under `data/processed/venue/`.
**Conflict rule:** where the journal's *written guidelines* and its *example PDF/template* disagree,
the written guidelines win (per the project's operating contract).

| # | Topic | Rule (quoted) | Source URL | Confidence |
|---|---|---|---|---|
| V1 | Journal identity | "iSys - Journal of Information Systems is a peer-reviewed and open-access scientific journal dedicated to the field of Information Systems (IS). It is a scientific publication of the Special Committee on Information Systems (CESI) of the Brazilian Computer Society (SBC)." | https://sol.sbc.org.br/journals/index.php/isys/about | certain |
| V2 | **Scope (decisive)** | "The field of Information Systems understands technology as a means rather than an end, emphasizing the phenomena that arise from its development, adoption, and use across organizational and social contexts." | https://sol.sbc.org.br/journals/index.php/isys/about | certain |
| V3 | **Scope (desk-rejection risk)** | "A substantial number of submissions received by iSys - Journal of Information Systems are returned during desk review due to misalignment with the Information Systems (IS) field. Many manuscripts treat information systems as a synonym for software systems, applications, or technical computing artifacts, which does not fully reflect the scope of the discipline." | https://journals-sol.sbc.org.br/index.php/isys/understanding-is | certain |
| V4 | Scope — out-of-scope examples | "Submissions that focus exclusively on technical aspects of computing without addressing organizational or societal contexts are generally outside the scope of iSys." Listed examples include "Programming techniques or frameworks" and "Software architecture … focused solely on technical performance". | https://journals-sol.sbc.org.br/index.php/isys/understanding-is | certain |
| V5 | Scope — how a technical artifact *can* fit | "Technical artifacts (systems, tools, architectures, or models) may fall within the scope of iSys when they are positioned within a broader IS research context. This is particularly common in Design Science Research (DSR) … the manuscript should clearly describe: The organizational or societal problem addressed; The design rationale of the artifact; The evaluation of the artifact in a relevant context; The implications for organizations, users, or society." | https://journals-sol.sbc.org.br/index.php/isys/understanding-is | certain |
| V6 | IS-literature expectation | "Ensure that relevant related work was searched on iSys and SOL (SBC OpenLib) and considered in the submission." and "Submissions must demonstrate proper coverage of SOL (SBC OpenLib) literature." | https://sol.sbc.org.br/journals/index.php/isys/about/submissions | certain |
| V7 | IS literature list | "National venues and research agendas: iSys …, Brazilian Symposium on Information Systems (SBSI), … EnANPAD …, and the Grand Challenges in Information Systems Research in Brazil (GranDSI-BR 2026–2036)". Leading IS journals named: MISQ, ISR, EJIS, ISJ, JIT, JSIS, I&M, DSS. IS conferences: ICIS, ECIS, AMCIS, PACIS. | https://sol.sbc.org.br/journals/index.php/isys/about/submissions | certain |
| V8 | Template | "The manuscript is submitted in PDF, following the official iSys template" / "Submissions must use the official iSys template (the LaTeX version is highly preferred)" / "Submissions not using the template are subject to desk rejection." | https://sol.sbc.org.br/journals/index.php/isys/about/submissions | certain |
| V9 | Template artefact | `Template_LaTeX_iSys_2026_Preferred.zip` (Drive file id `1MXeux9NNOIv-cai2Fsn0m7kcdjqpb61L`), sha256 prefix `c852b3e3a4737448`, 137,893 bytes. Contains `sbc2025.cls`, `apalike-sol.bst`, `main-en.tex`, `refs.bib`, `sectsty.sty`, `aas_macros.sty`, `sol.jpg`. | https://drive.google.com/drive/folders/1N6UsfqLkN8hILbBW3NPgOsfj5iH-JyMR | certain |
| V10 | Page length | "Files must be submitted in PDF and should have a minimum of 15 pages" / "should have a minimum of 15 pages." **No maximum length is stated anywhere on the pages examined.** | https://sol.sbc.org.br/journals/index.php/isys/about/submissions | certain for the minimum; **maximum unknown** |
| V11 | Language | "iSys prefers manuscripts written in English" / "Manuscripts may be submitted in English or Portuguese." / "Title: must always be provided in English (mandatory)." | https://sol.sbc.org.br/journals/index.php/isys/about , …/about/submissions | certain |
| V12 | Abstract | "Every abstract, regardless of the paper being fully written in Portuguese or English, must be written in English (150–250 words)." "Abstracts/Resumo should be structured and briefly cover context, objective, method, results, and conclusion/contributions." "Remember to keep Abstract (and Resumo) in only one paragraph (without breaking lines)." | https://sol.sbc.org.br/journals/index.php/isys/about/submissions | certain |
| V13 | Keywords | "Provide 3–6 keywords (palavras-chave)." | https://sol.sbc.org.br/journals/index.php/isys/about/submissions | certain |
| V14 | Reference style | "References must follow the iSys template style (based on APA)." "Include DOIs whenever available." "All cited works must appear in the reference list and vice versa." "Where available, URLs for the references have been provided." | https://sol.sbc.org.br/journals/index.php/isys/about/submissions | certain |
| V15 | Mandatory post-conclusion sections | "All papers, after Final Remarks, must include mandatory declaration sections: Authors' Contributions (CRediT taxonomy); Competing Interests; Funding; Availability of Data and Materials; Acknowledgments (if applicable); References". The submission checklist separately states: "Mandatory subsections are included: Acknowledgments, Authors' Contributions (CRediT), Competing Interests, Availability of data and materials, Further relevant information …, and Funding." | https://sol.sbc.org.br/journals/index.php/isys/about/submissions | certain, but the two lists are **not identical** (see ambiguity A2) |
| V16 | **AI disclosure** | "AI tools cannot be listed as authors." "Their use must be transparently disclosed (tool, purpose, verification)." "AI must not be used to fabricate data, citations, or analysis." "Any use of AI/LLMs (e.g., ChatGPT, Copilot) is transparently described, including the tool, purpose, and author verification." Example given: "The authors used ChatGPT (OpenAI, 2025) to improve grammar. All suggestions were reviewed and approved by the authors." | https://sol.sbc.org.br/journals/index.php/isys/about/submissions | certain |
| V17 | **Double-anonymous review** | "iSys adopts a double-anonymous peer review process." "Ensure that the submitted manuscript is fully anonymized … removing all information (in the text, references, acknowledgments, and file metadata) that may directly or indirectly identify the authors." "Avoid self-identifying references … When citing your own work, use neutral phrasing". "Omit project names, institutional references, or links that may directly identify the authors or research group." | https://sol.sbc.org.br/journals/index.php/isys/about/submissions | certain |
| V18 | Cover letter | "All submissions must include a cover letter addressing: Scope …; Background …; Open Science …; Research Highlights: Up to five key contributions …; Authorship: Contributions of each author (CRediT taxonomy); Competing Interests". | https://sol.sbc.org.br/journals/index.php/isys/about/submissions | certain |
| V19 | Figures/tables/accessibility | "Figures must be submitted in high resolution (300 dpi) in PNG, JPG, EPS, or TIFF." "Tables must be editable (not embedded as images)." "Captions must be self-explanatory." "Ensure that color images are accessible to all, including those with impaired color vision." | https://sol.sbc.org.br/journals/index.php/isys/about/submissions | certain |
| V20 | Licensing / charges | "iSys is free of charges for both authors and readers." "All articles are published under the CC BY 4.0 license. Authors retain copyright and full publishing rights." "No APCs (Article Processing Charges)." | https://sol.sbc.org.br/journals/index.php/isys/about/submissions | certain (matches the brief's "none to submit or to read") |
| V21 | Preprints / pre-registration | "Authors are allowed to deposit preprints on non-commercial repositories (e.g., arXiv, OSF). Upon acceptance, authors should update the preprint with the article's DOI and citation." | https://sol.sbc.org.br/journals/index.php/isys/about | certain — **OSF pre-registration of docs/method.md is permitted** |
| V22 | Ethics statement | "The manuscript explicitly explains how ethical issues were addressed, including ethics committee approval when applicable." "Manuscripts must explicitly indicate how the ethical issues of the research were addressed and managed". | https://sol.sbc.org.br/journals/index.php/isys/about/submissions , …/about | certain |
| V23 | Open science | "Authors are strongly encouraged to make datasets, code, and supplementary materials publicly available." "Authors are encouraged to deposit datasets, software, appendices, and transcripts in trusted repositories (e.g., Zenodo, OSF, GitHub)." | https://sol.sbc.org.br/journals/index.php/isys/about/submissions | certain |
| V24 | Review criteria | "Reviewers assess manuscripts according to the following criteria: 1) Novelty and originality, 2) Rigor and methodological soundness, 3) Relevance to the Information Systems field, 4) Transparency, replicability, and reproducibility, and 5) Presentation quality and clarity." | https://sol.sbc.org.br/journals/index.php/isys/about/submissions | certain |
| V25 | Desk review | "All manuscripts submitted first undergo a desk review by the Editors-in-Chief … At this stage, submissions are checked for scope alignment, completeness, formatting, and compliance with the Authors Guidelines. Manuscripts that do not meet these requirements may be desk rejected without external review." | https://sol.sbc.org.br/journals/index.php/isys/about | certain |
| V26 | Similarity check | "Submissions are checked using similarity-detection software." | https://sol.sbc.org.br/journals/index.php/isys/about | certain |
| V27 | Metadata after acceptance | Camera-ready must restore "all authors' names, affiliations, emails, and ORCID identifiers that were omitted during the double-anonymous review process." | https://sol.sbc.org.br/journals/index.php/isys/about/submissions | certain |
| V28 | Separate references file | After acceptance: "Authors must also submit a separate file (.txt or .docx) containing the complete list of references, formatted according to the iSys template." | https://sol.sbc.org.br/journals/index.php/isys/about/submissions | certain |
| V29 | Qualis | "Classified as Qualis A4 by the Brazilian federal agency CAPES …, considering the four-year period 2021-2024." | https://sol.sbc.org.br/journals/index.php/isys/about | certain |

## Ambiguities to disclose in the cover letter

- **A1 — Page limit.** A minimum of 15 pages is stated; **no maximum** appears on any page examined
  (Submissions, About, IS-nuances, Aims and Scope). The brief's requirement "within the venue limit"
  is therefore satisfied by *meeting or exceeding* 15 pages. We will state our final page count in the
  cover letter.
- **A2 — Mandatory declaration sections.** Two lists are given and they differ: the checklist
  ("Acknowledgments, Authors' Contributions (CRediT), Competing Interests, Availability of data and
  materials, Further relevant information, Funding") vs. the structure list ("Authors' Contributions
  (CRediT), Competing Interests, Funding, Availability of Data and Materials, Acknowledgments (if
  applicable), References"). We will include the **union of both**, which satisfies either reading.
- **A3 — Anonymity vs. reproducible public package.** V17 requires omitting "project names … or links
  that may directly identify the authors", while V23/Open-Science requires a public replication
  package. A GitHub URL under the author's own account is self-identifying. Resolution: submit an
  **anonymized mirror** (e.g. anonymized.4open.science) during review and cite the canonical public
  repository only in the camera-ready. To be declared in the cover letter.
- **A4 — "Declaration of AI-Assisted Use in Writing" placement.** The project contract mandates this
  section *immediately before References*. iSys mandates a set of declaration sections after "Final
  Remarks", with References last. These are compatible: we place the AI declaration as the final
  declaration subsection, immediately before References. iSys's own label for this content is "Further
  relevant information"; we will title the subsection so that it satisfies both (see paper §Declarations).
- **A5 — IS scope.** See V2–V5. The paper must be positioned as IS research, not as an SE tooling
  study. This is a **design decision referred to the human** (see `docs/GATE-1.5-REPORT.md`).

## Consequences for our build

1. Build must use `sbc2025.cls` + `apalike-sol.bst` from the official template — **not** SBC's generic
   `sbc-template`. Bibliography must be produced by **BibTeX with `apalike-sol.bst`** (APA), not
   `plain`/`unsrt`/biblatex+biber. This overrides the brief's assumption that biber is the reference
   engine.
2. Minimum 15 pages is a *floor*; the paper must not be shorter.
3. Because review is double-anonymous and the paper name contains "BDD", the repository name
   `bdd-specification-drift` is itself a self-identifying link → anonymized mirror needed for review.
4. Related work must include iSys/SOL material and IS-venue literature, which the current S1 search
   faces do **not** cover. A fifth search face on IS literature (business-IT alignment, requirements
   traceability, design science, IS quality) is required before the paper is written.
