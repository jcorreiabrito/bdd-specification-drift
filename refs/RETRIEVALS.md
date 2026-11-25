# refs/RETRIEVALS.md — non-trivial retrieval log

Required by the operating contract: *"Log every non-trivial retrieval in refs/RETRIEVALS.md."*
Every HTTP response is also machine-logged in `data/raw/INDEX.jsonl` with URL, UTC timestamp,
SHA-256, byte size and saved path. This file records the retrievals that required a decision,
a workaround, or that materially changed the study.

**Access rules observed:** no shadow libraries (no Sci-Hub, LibGen, Anna's Archive). Paywalled work
was reached only through open-access copies, institutional repositories, author pages, or not at all.

---

## Venue documents (decision-critical)

| Resource | URL | Date | Note |
|---|---|---|---|
| iSys About / Focus and Scope | `https://sol.sbc.org.br/journals/index.php/isys/about` | 2026-11-25 | Revealed the **IS-scope** problem (gate report §2) |
| iSys Submissions / Author Guidelines | `.../about/submissions` | 2026-11-25 | 29 rules extracted into `submission/VENUE-RULES.md` |
| **Understanding the IS nuances** | `https://journals-sol.sbc.org.br/index.php/isys/understanding-is` | 2026-11-25 | States that many submissions are desk-returned for treating IS as software engineering |
| SBC Code of Conduct | `https://sol.sbc.org.br/index.php/indice/conduta` | 2026-11-25 | Compliance required by the brief |
| **Official iSys 2026 LaTeX template** | Google Drive file id `1MXeux9NNOIv-cai2Fsn0m7kcdjqpb61L` | 2026-11-25 | 137,893 B, sha256 `c852b3e3a4737448…`. Drive folder pages are JS-rendered; the file id was recovered by parsing the embedded `_DRIVE_ivd` payload (`scripts/probe_drive.py`) |

> The template ZIP is **not committed** (vendor artefact, and `paper/template/` is gitignored).
> `scripts/probe_drive.py` reproduces the discovery; the file id above is the permanent handle.

## Literature retrievals requiring a workaround

| Work | How it was obtained | Note |
|---|---|---|
| **Li, West, Escalona, Durelli (2015)**, *Mutation testing in practice using Ruby* | IEEE Xplore abstract page (abstract); **open-access slide deck** `https://mutation-workshop.github.io/2015/mutationTestingInPractice.pdf` | The paper is paywalled, but the authors' Mutation-2015 slides are openly hosted and carry the result table (1,716 mutants, MS 0.78, 97.2 % SC). Extracted with `scripts/pdf_extract.py`. **Decisive:** the deck never mentions Cucumber, which is why Li et al. is *not* described as a BDD study. |
| **dos Santos et al. (2024)**, AAT4IRS | Frontiers in Robotics and AI (open access) | The closest prior work; invalidated the strongest form of our novelty claim. |
| **Zampetti et al. (2020)**, IST | Publisher abstract only | **No open-access copy exists** (Unpaywall reports none); the authors' institutional repository returned Cloudflare 403; ScienceDirect paywalled. Cited from its unusually detailed structured abstract, row marked `crossref+abstract`. **Do not over-claim.** |
| **Kim et al. (2021)**, FSE — disabled tests | Open-access copies | 3,111 disabling changes / 122 K commits / 41 % never re-enabled. |
| **Binamungu & Maro (2023)**, JSS | arXiv preprint converted to text | The 166-paper BDD mapping study. Our own regex probe found `mutat` **zero** times in the full text — this is the strongest single line of evidence for the gap. |
| Springer / ACM / IEEE full texts (several) | 403 (Cloudflare / bot gating) | Worked around with `web.archive.org` replays of abstracts and open-access mirrors where available, otherwise cited from abstract and marked as such. |
| **van Deursen et al. (2001)** | Open-access CWI report PDF | **Has no DOI anywhere.** Protocol forbids citing DOI-less work, so it is documented in `lit/notes.decay.md §DOI-less but essential`, not in `refs/verified.csv`. |

## Data / infrastructure retrievals

| Resource | URL | Note |
|---|---|---|
| Sampling frame | `https://github.com/topics/<slug>?l=<lang>&page=<n>` ×252 | Token-free enumeration (`scripts/enumerate_frame.py`); snapshot hash recorded in `data/frame/FRAME.md` |
| API reachability survey | pypi.org, registry.npmjs.org, repo.maven.apache.org, api.crossref.org, services.gradle.org, api.adoptium.net, api.osf.io | `scripts/probe_gh_surfaces.py`, `scripts/fetch.py`; results in `TEAM.md §3` |
| Maven 3.9.9 / Gradle 8.10.2 | Maven Central / services.gradle.org | Vendored into `tools/jvm/` (gitignored) because neither is installed on the host |
| Version discovery | `maven-metadata.xml` for pitest-maven, pitest-junit5-plugin, cucumber-java, junit-platform-suite | Versions were **queried, not assumed** (PIT 1.30.2, plugin 1.2.3, Cucumber 8.1.0, JUnit 6.1.3) |

## Known retrieval failures (disclosed, not hidden)

- **ScienceDirect / IEEE Xplore / ACM DL / Springer full texts**: largely inaccessible from this host.
- **DBLP API**: bot-blocked → Portuguese-language venues (SBES, CBSOFT) could not be swept.
- **Semantic Scholar API**: HTTP 429 under load; used only opportunistically.
- **`iris.unisannio.it`** (Zampetti accepted manuscript): Cloudflare 403.
- **GitHub code search**: requires authentication; unavailable without a token.
