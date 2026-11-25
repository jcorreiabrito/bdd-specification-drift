# TEAM.md â€” live coordination board

**Project:** *Do Public BDD Suites Still Work as Oracles? A Mutation-Based Study of Specification Drift in Cucumber-Style Test Suites*
**Venue:** iSys â€” Revista Brasileira de Sistemas de InformaÃ§Ã£o / Journal of Information Systems (SBC/CESI, Qualis A4)
**Workspace:** `C:\Users\jvtri\OneDrive\Documentos\Projetos\bdd-specification-drift`
**Lead / orchestrator:** `lead` (root agent)
**Last updated:** 2026-11-25

> This file is maintained by the Lead only. Subagents must not edit it (see `docs/RESEARCH_PROTOCOL.md` Â§3).
> Agent names below are the *real* subagent identifiers from the runtime, not role-play.

---

## 1. Phase status

| Phase | Content | Status |
|---|---|---|
| P0 | Novelty check (S1), venue rules, environment inventory, repo init, secret guard | **DONE** |
| P1 | `docs/method.md`: sampling plan, metrics, mutation protocol, statistics, power analysis | **DONE** (`docs/method.md`, power table verified) |
| P1.5 | Pilot: real funnel yield, tool feasibility | **DONE** — 170 screened, 9 eligible (5.3 %, CI 2.8-9.8 %); JS + Java strata proven |
| **GATE** | **Human stop: novelty note + method.md + power analysis + pilot yield + tool feasibility** | **REACHED — AWAITING HUMAN DECISION** (`docs/GATE-1.5-REPORT.md`) |
| P2 | Full sampling pipeline + attrition log | blocked by gate |
| P3 | Mutation + metric measurement | blocked by gate |
| P4 | Statistics + figures | blocked by gate |
| P5 | Manuscript | blocked by gate |
| P6 | Red-team + revision | blocked by gate |
| P7 | Compliance + submission folder | blocked by gate |

---

## 2. Roster â€” actual agents

| Agent | Contract role | Task | Status |
|---|---|---|---|
| `lead` | Orchestrator, owns correctness end to end | venue rules, build system, method, integration, paper | **running** |
| `lit-bdd` | S1 (facet: BDD effectiveness) | first attempt | **failed** â€” restarted as `lit-bdd2` |
| `lit-bdd2` | S1 (facet: BDD effectiveness & Gherkin quality) | `refs/verified.bdd.csv`, `lit/notes.bdd.md` | done (17 refs) |
| `lit-mutation` | S1 (facet: mutation testing as oracle measure) | `refs/verified.mutation.csv`, `lit/notes.mutation.md` | done (18 refs) |
| `lit-decay` | S1 (facet: test decay / erosion / disabled tests) | `refs/verified.decay.csv`, `lit/notes.decay.md` | done (27 refs) |
| `lit-intersect` | S1 (facet: BDD Ã— mutation intersection â€” novelty-critical) | `refs/verified.intersect.csv`, `lit/notes.intersect.md` | running |

Dispatched and finished: s2-method -> `docs/method.md`.

Not yet dispatched (deliberately serialised behind the gate):
S2 methodologist, S3 artifact engineer, S4 experiment runner, S5 red-team reviewer, S6 compliance editor.

**Additional S1 facet identified by the Lead and NOT yet dispatched:** Information Systems literature
(businessâ€“IT alignment, requirements traceability, design science, IS quality). Required by the venue
(see `submission/VENUE-RULES.md` V6â€“V7); the four running facets are all software-engineering venues
and cannot satisfy it.

---

## 3. Environment facts (measured, 2026-11-25 â€” do not re-litigate)

| Capability | State | Consequence |
|---|---|---|
| Shell | Windows PowerShell **5.1**; there is no `pwsh` binary | never invoke `pwsh` recursively |
| `git` | 2.44.0 | OK; GitHub remote is **empty** |
| Python | 3.12.4 + pip 26.0.1 | OK |
| Node / npm / pnpm | 24.11.0 / 11.6.1 / 12.18.0 | OK |
| Java | **JDK 22 only**, `JAVA_HOME` unset | older Cucumber-JVM corpora may not build |
| Maven / Gradle | **absent** | must rely on in-repo `mvnw` / `gradlew` wrappers |
| Docker | **absent** | **no build isolation** â€” a major reproducibility limitation |
| Perl | **absent** | `latexmk` is unusable by design |
| MiKTeX | 25.12, `pdflatex`/`bibtex` OK | must pass `--disable-installer` (installer hangs) |
| `curl.exe`, `Invoke-WebRequest` | **blocked** (TLS reset / http_code 000) | use Python `urllib` |
| PyPI, npm, Maven Central, GitHub, codeload, Gradle, OSF | reachable | OK |
| GitHub REST API | reachable, **unauthenticated, 60 req/h, exhausted** | **no token supplied â€” blocks any API-based sampling frame** |
| File sandbox | writes only inside the workspace | npm cache + pip userbase must be workspace-local |

---

## 4. Decisions and deviations log

| # | Date | Decision | Reason |
|---|---|---|---|
| D1 | 2026-11-25 | Build uses `pdflatex --disable-installer` + `bibtex` with `apalike-sol.bst`, **not** biber/latexmk | no Perl; MiKTeX installer hangs under sandbox; venue template is BibTeX+APA |
| D2 | 2026-11-25 | Document preamble must load `\usepackage{lmodern}` | official `sbc2025.cls` comments it out â†’ bitmap T1 fonts â†’ microtype font-expansion fatal error |
| D3 | 2026-11-25 | All tool caches (`npm_config_cache`, `PYTHONUSERBASE`) redirected into the workspace | sandbox denies writes to AppData; npm EPERM and venv ensurepip failures proved it |
| D4 | 2026-11-25 | S1 relaunched `lit-bdd` as `lit-bdd2` with incremental-write instruction and a narrower brief | first attempt crashed leaving no output |

