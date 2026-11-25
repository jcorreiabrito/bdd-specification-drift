# docs/DEVIATIONS.md — deviations from the brief and from `docs/method.md`

**Purpose.** The operating contract requires that any deviation from `docs/method.md` after the P1
gate be logged here with a reason and a timestamp, and disclosed in the paper. This file also records
**constraints imposed by the environment** that force a departure from the original plan, because the
paper must disclose those too even though they are not "method changes" in the narrow sense.

**Status: the P1 gate has NOT closed.** No corpus has been measured, so no post-gate deviation can
yet exist. Everything below is either (a) an environment-forced constraint discovered during P0–P1.5,
or (b) a pre-gate decision awaiting human approval.

---

## A. Environment-forced constraints (must be disclosed in the paper)

| # | Plan said | What actually happened | Reason | Consequence for the paper |
|---|---|---|---|---|
| **E1** | Use the GitHub API with a token; cache responses under `data/raw/` | **No token was available.** Unauthenticated REST is 60 req/h and was already exhausted | Token never supplied; the brief assumed one | The sampling frame is enumerated from public GitHub **topic pages** (token-free, 252 pages, snapshot-hashed) instead of code search. The frame is therefore *"repositories that adopted at least one declared BDD-related topic tag on the snapshot date"*. **Topic-tagging bias must be stated as a threat to external validity.** |
| **E2** | Per-repo build/run harness with isolated builds | **Docker is absent from the host**; only JDK 22 is installed; Maven and Gradle are absent | Host capability | No build isolation. Java corpora targeting 8/11/17 may fail on JDK 22 and are categorised `tool_incompatibility`, distinct from `dependency_rot`. Cross-repo toolchain contamination is a live threat, mitigated by per-repo cache localisation plus a repeatability probe (method §14 T10). Maven 3.9.9 and Gradle 8.10.2 were **vendored into the repository** to make the Java stratum possible at all. |
| **E3** | Mutation tools drive the BDD runner | **Tools cannot run under the file sandbox**: Stryker failed with `EPERM: spawn` (errno −4048) under `workspace-write` | Sandbox forbids piped child processes by design | All mutation runs execute unsandboxed or in CI. Disclosed so that reproduction is realistic. Recorded in `results/RUNLOG.md` R001. |
| **E4** | Three language strata: Java, JS/TS, Python | **Python stratum not established.** PyPI resets connections (2–3 of 5 attempts); mutmut 3.x is coupled to pytest and does not accept an arbitrary BDD runner | Network filtering + tool design | Python is reported as `at risk`, not silently dropped (RUNLOG R003). If it cannot be established, Python is dropped as a stratum and **reported as a limitation**, per the brief. |
| **E5** | `latexmk` build via `build.ps1` | `latexmk` is unusable; the official `sbc2025.cls` omits `lmodern` and microtype dies on bitmap fonts; the MiKTeX installer hangs under the sandbox | No Perl; class defect; sandbox | `build.ps1` was written from scratch: `pdflatex --disable-installer` ×3 + `bibtex` with `apalike-sol.bst`, and the document must load `\usepackage{lmodern}`. Documented in `build.ps1` header and `submission/VENUE-RULES.md`. |
| **E6** | Reference engine = biber/bibtex as convenient | **BibTeX only**, with the venue's `apalike-sol.bst` (APA) | The iSys template ships a BibTeX `.bst`, not a biblatex style | Reference formatting is dictated by the venue template, not by preference. |
| **E7** | Shadow libraries excluded (per brief) | Enforced: no shadow library was used. Paywalled work was reached via open-access copies, institutional repositories, Wayback replays of abstracts, or not at all | Brief + integrity rule | Several works are cited from **abstracts only** (notably Zampetti et al. 2020), and each such work is marked `crossref+abstract` in `refs/verified.csv`. The paper must not over-claim from abstract-only sources. |

## B. Pre-gate findings that change the design, pending human decision

| # | Finding | File | Awaiting |
|---|---|---|---|
| **G1** | iSys is an **Information Systems** journal; a pure SE mutation-testing paper is at high desk-rejection risk. Options: reframe as IS/DSR, submit as-is, or change venue. | `submission/VENUE-RULES.md` V2–V5; `docs/GATE-1.5-REPORT.md` §2 | **D1** |
| **G2** | Pilot yield is **5.3 %** (95 % CI 2.8–9.8 %); the eligible set is dominated by BDD **tooling** repositories, not applications with a domain layer, so the "mutants as business-rule proxy" construct is threatened. | `data/pilot/PILOT.md`; gate report §5.1 | **D2, D3** |
| **G3** | `"specification drift"` is **not** an established term; the paper must coin and define it as a specialisation of architectural drift, with hedging. | `lit/novelty.md` §5 | naming decision, gate report §1 |
| **G4** | Novelty survives only as a **conjunction**; AAT4IRS (2024) already mutation-tested a BDD suite once. | `lit/novelty.md` | acknowledgement in the introduction |

## C. Post-gate deviations

_None yet — the gate has not closed._
