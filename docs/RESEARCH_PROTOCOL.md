# Research Protocol — binding for every agent on this project

Project: *Do Public BDD Suites Still Work as Oracles? A Mutation-Based Study of Specification Drift in Cucumber-Style Test Suites*

## 1. Integrity rules (non-negotiable)

1. **Never cite a paper you have not opened.** "Opened" means you retrieved the abstract page, the PDF, or the publisher landing page and read at least the abstract plus the section you quote.
2. **Every reference needs a Crossref-verified DOI** and a row in your `refs/verified.<tag>.csv`. No DOI ⇒ no citation. Delete it.
3. **Never invent a quantitative value.** If you cannot retrieve a number, write `NR` (not retrievable). Do not estimate, do not interpolate, do not "approximately".
4. **Never fabricate a quotation.** The `supporting_sentence` field must be an exact substring of the source text you retrieved. If you paraphrase, prefix with `PARAPHRASE:`.
5. **Do not use shadow libraries** (Sci-Hub, LibGen, Anna's Archive). Use open-access versions, preprints (arXiv), author pages, publisher landing pages, or the Crossref/Unpaywall API.
6. **AI cannot be an author.** This project's paper carries a mandatory "Declaration of AI-Assisted Use in Writing" section.

## 2. Network reality on this host (measured 2026-11-25)

| Endpoint | Status | How to use |
| :--- | :--- | :--- |
| `curl.exe` | **BLOCKED** (http_code 000) | never use |
| PowerShell `Invoke-WebRequest` | **BLOCKED** (TLS reset) | never use |
| Python `urllib` / `requests` | **WORKS** | primary HTTP method |
| `web_search` / `web_fetch` tools | **WORKS** | primary discovery method |
| `api.crossref.org` | WORKS | DOI verification |
| `raw.githubusercontent.com` | WORKS | file retrieval |
| `registry.npmjs.org` | WORKS | npm |
| `repo.maven.apache.org` | WORKS | Maven |
| `pypi.org` | **BLOCKED** (WinError 10054) | Python packages may fail to install |
| `api.semanticscholar.org` | WORKS but 429-prone | back off and retry |
| GitHub REST API | WORKS, unauthenticated quota **60 req/h, currently exhausted** | do not burn quota |

HTTP from Python:

```powershell
python -c "import urllib.request,json; r=urllib.request.urlopen('https://api.crossref.org/works/10.1016/j.infsof.2020.106311',timeout=30); print(r.read().decode()[:2000])"
```

## 3. Output contract

Write **only** to your own tagged files, to avoid merge conflicts:

- `refs/verified.<TAG>.csv` — one row per reference
- `lit/notes.<TAG>.md` — structured notes
- `lit/matrix.<TAG>.csv` — the comparison matrix rows

Never edit files owned by another agent (including `TEAM.md`, `refs/verified.csv`, `docs/method.md`). The Lead merges.

### CSV schema for `refs/verified.<TAG>.csv`

Header exactly:

```
key,title,authors,year,venue,doi,retrieval_date,source_url,verified_via,supporting_sentence,relevance
```

- `key`: BibTeX key, form `FirstauthorYYYYshortslug` (e.g. `Zampetti2020Demystifying`), lowercase ASCII, no spaces.
- `authors`: `Surname, I.; Surname, I.` (max 6 then `et al.`).
- `year`: 4 digits.
- `doi`: bare DOI, no `https://doi.org/` prefix.
- `retrieval_date`: `YYYY-MM-DD` (host date).
- `verified_via`: one of `crossref+pdf`, `crossref+abstract`, `crossref+publisher`.
- `supporting_sentence`: exact quoted sentence supporting the claim you attribute to the paper; or `PARAPHRASE: ...`.
- `relevance`: max 25 words, why it matters to *this* study.
- Quote all fields containing commas. Escape `"` as `""`.

### `lit/notes.<TAG>.md` structure

```
# <TAG> — literature notes
## Scope searched
(query strings used, databases hit, date)
## Papers opened
### <key> — <Title> (<Venue> <Year>)
- **What it does:**
- **Method / data:**
- **Key findings (verbatim numbers only):**
- **What it does NOT answer for us:**
- **Threat it poses to our novelty:** none | minor | major
## Search log
- query → #hits screened → #opened → #kept
## Dead ends
(papers/claims that looked relevant but were not; so we do not re-search them)
```

## 4. Novelty discipline

The claim under test is:

> **"The mutation-based oracle strength of public BDD suites, and its erosion over time, has not been measured at scale."**

It is **NOT** "BDD quality has not been studied". BDD quality *has* been studied. Your job is to find whether anyone has already combined (a) public Cucumber-style suites, (b) mutation analysis restricted to the domain layer, (c) separation of BDD-only from full-suite kill, (d) a longitudinal/erosion component.

If a paper already does this, say so **explicitly and prominently** under a `## NOVELTY KILLED` heading at the top of your notes. Reporting that is a success, not a failure.

## 5. Honesty about coverage

State plainly which searches you could not complete (paywall, blocked host, quota). A gap you could not search is a limitation of the review, and the Lead must know.
