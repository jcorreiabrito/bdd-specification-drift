# results/RUNLOG.md — append-only evidence log

Every quantitative claim in the paper must trace to an entry here. An entry is
valid only if it records: **command**, **UTC timestamp**, **git commit SHA**,
**host**, **seed**, **tool versions**, and **where the output went**.

Rules:
- Append only. Never edit or delete a past entry; supersede it with a new one.
- Record failed and abandoned runs too — the attrition log depends on them.
- `git_sha` is the commit of the *analysed harness code*, not of the corpus repo.
  Corpus repository identities and commit SHAs live in `data/corpus/LOCKFILE.csv`.

## Environment (constant unless an entry says otherwise)

| Fact | Value |
|---|---|
| Host | `BOOK-FLG1TLH8V5` |
| OS | Microsoft Windows NT 10.0.26300.0 |
| CPU | 13th Gen Intel Core i5-1335U |
| RAM | 15.7 GB |
| Python | 3.12.4 |
| Node | v24.11.0 |
| npm | 11.6.1 |
| Java | Oracle JDK 22.0.1 (`JAVA_HOME` set per command) |
| Maven | Apache Maven 3.9.9 (vendored at `tools/jvm/maven/`, local repo `.m2repo/`) |
| Gradle | 8.10.2 (vendored at `tools/jvm/gradle/`, `GRADLE_USER_HOME=.gradle-home/`) |
| LaTeX | MiKTeX 25.12; `pdflatex`/`bibtex` used with `--disable-installer` |
| Per-shell note | Shell is Windows PowerShell 5.1; there is no `pwsh` binary |

---

## R001 — JS/TS mutation harness feasibility (Stryker × Cucumber)

- **UTC**: 2026-11-25T11:54:56Z
- **git_sha**: `b7115a4` (harness commit; smoke project untracked at run time)
- **seed**: n/a (no sampling in this probe)
- **purpose**: prove that Stryker can be driven by a Cucumber-JS suite and that
  coverage-conditioned mutation scoring works, before committing the design.
- **command**:
  ```powershell
  cd pilot\smoke-js
  npx --no-install cucumber-js                       # baseline suite
  npx --no-install stryker run stryker.conf.json      # mutation analysis
  ```
- **tool versions**: `@stryker-mutator/core` 10.1.1, `@stryker-mutator/cucumber-runner` 10.1.1,
  `@cucumber/cucumber` 12.2.0, Node v24.11.0.
- **config**: `pilot/smoke-js/stryker.conf.json` — `testRunner: "cucumber"`,
  `coverageAnalysis: "perTest"`, `mutate: ["src/**/*.js"]`, `timeoutMS: 30000`, `concurrency: 2`.
- **baseline result**: 4 scenarios, 16 steps, all passed.
- **mutation result**: 43 mutants — 31 killed, 12 survived, **0 no-coverage**, 0 timeout, 0 errors.
  Mutation score **72.09 %** (total and covered identical, because coverage was complete).
- **artifact**: `results/pilot/smoke-js-mutation.json` (Stryker JSON reporter).
- **repeatability**: run twice, identical counts both times (exit 0).
- **what this proves**: the JS/TS stratum is tool-feasible; Stryker reports a
  `NoCoverage` status separately, so the mandatory covered-vs-all conditioning
  (RQ2) is measurable; per-mutant test attribution names the individual Cucumber
  scenarios, so BDD-only vs full-suite differential kill is computable.
- **what this does NOT prove**: that the same works on a real third-party
  repository (dependency rot, TS build steps, monorepos). That is the pilot's job.
- **environment caveat**: under the earlier `workspace-write` policy this command
  failed with `EPERM: spawn` (errno -4048) because Stryker launches piped child
  processes. The run recorded above was executed under the `danger-full-access`
  policy. **Any reproduction must therefore run unsandboxed, or in CI.**

### Observed survivors (illustrative, not a finding)
All 12 survivors are boundary/equality mutants in `src/pricing.js`, e.g.
`orderTotal > 250` → `orderTotal >= 250` and `orderTotal > 750` → `>= 750`.
The suite exercises those branches but never at the boundary value, i.e. the
scenarios are *reachable but not probing*. This is a concrete, if anecdotal,
instance of the oracle-weakness phenomenon the study targets.

---

## R002 — Java mutation harness feasibility (PIT × Cucumber-JVM)

- **UTC**: 2026-11-25T11:56:17Z
- **git_sha**: `b7115a4` (smoke project untracked at run time)
- **seed**: n/a (no sampling in this probe)
- **purpose**: prove that PIT can drive a Cucumber-JVM suite through the JUnit
  Platform engine and produce a mutation score, before committing the design.
- **command**:
  ```powershell
  cd pilot\smoke-java
  $env:JAVA_HOME="C:\Program Files\Java\jdk-22"
  mvn -B -Dmaven.repo.local=<repo>\.m2repo test                    # baseline
  mvn -B -Dmaven.repo.local=<repo>\.m2repo pitest:mutationCoverage # mutation
  ```
  (`mvn` = vendored Apache Maven 3.9.9 at `tools/jvm/maven/`.)
- **tool versions**: PIT `pitest-maven` 1.30.2, `pitest-junit5-plugin` 1.2.3,
  `io.cucumber:cucumber-java` 8.1.0, `cucumber-junit-platform-engine` 8.1.0,
  JUnit Platform 6.1.3, JDK 22.0.1, `maven.compiler.release=17`.
- **config**: `pilot/smoke-java/pom.xml` — `targetClasses=smoke.pricing.*`,
  `targetTests=smoke.RunCucumberTest`, operators = PIT `DEFAULTS` (probe only).
- **baseline result**: BUILD SUCCESS, Cucumber features discovered and executed.
- **mutation result**: **19 mutants — 14 killed (74 %), 0 with no coverage**,
  test strength 74 %, line coverage of mutated classes 12/14 (86 %),
  29 tests ran (1.53 per mutation), total 5 s.
- **artifact**: `pilot/smoke-java/target/pit-reports/` (XML + HTML); console
  transcript `pilot/smoke-java/pitest.out.txt`.
- **what this proves**: the Java stratum is tool-feasible; PIT discovers individual
  Cucumber scenarios as tests (it names them in its timing block), so BDD-only vs
  full-suite differential kill is computable in Java as well as JS.
- **method-relevant observation**: PIT generated **19** mutants for the same domain
  logic on which Stryker generated **43** (R001). This is direct local evidence that
  mutation tools are not on a common axis, corroborating Kintis et al. (2018), and
  is why `docs/method.md` forbids pooling raw scores across languages.
- **environment caveat**: requires a vendored Maven and a workspace-local repository
  (`-Dmaven.repo.local`), because Maven is absent from the host and the file sandbox
  forbids writing to the default `~/.m2`.

---

## R003 — Python mutation harness feasibility (mutmut × behave/pytest-bdd)

- **status**: **not attempted to completion.** PyPI is unreliable on this host
  (measured 2–3 successful connections in 5 attempts, `ConnectionResetError 10054`);
  mutmut 3.x is also coupled to pytest rather than accepting an arbitrary BDD
  runner. Recorded as a stratum risk, not silently dropped.
