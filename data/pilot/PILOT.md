# P1.5 pilot — screening yield

- Frame size `N_frame`: **2552**
- Sampling seed: **20261125** (hash-ordered permutation of frame)
- Repositories attempted: **170**
- Eligible after static screen: **9** (5.3 %; 95 % Wilson CI 2.8–9.8 %)
- Extrapolated eligible pool in frame at this yield: **72–249** repositories

> **The frame as currently defined cannot reach the design target of n = 30.**
> At the upper 95 % bound this frame yields at most ~249 statically eligible repositories before any build attrition,
> and build attrition can only remove repositories. **This is a gate decision.**

## Funnel states

| State | n |
|---|---|
| excluded | 161 |
| eligible | 9 |

## Exclusion reasons (categorised)

| Reason | n | share |
|---|---|---|
| too_few_scenarios | 76 | 44.7 % |
| no_feature_files | 73 | 42.9 % |
| no_step_definitions | 6 | 3.5 % |
| licence_not_permissive | 4 | 2.4 % |
| clone_failed | 2 | 1.2 % |

## Scenario-count distribution (all attempted)

| scenarios | n |
|---|---|
| >=20 | 19 |
| 10-19 | 8 |
| 5-9 | 18 |
| <5 | 125 |

## Licence presence (all attempted)

| licence | n |
|---|---|
| `mit` | 102 |
| `none_found` | 58 |
| `isc` | 7 |
| `` | 2 |
| `agpl-3.0` | 1 |

## Eligible repositories

- `reqnroll/Reqnroll.VisualStudio` — 50 features, 997 scenarios, licence `mit`, build `Connectors/Reqnroll.VisualStudio.ReqnrollConnector.Generic/Reqnroll.VisualStudio.ReqnrollConnector.Generic.csproj;Connectors/Reqnroll.VisualStudio.ReqnrollConnector.Models/Reqnroll.VisualStudio.ReqnrollConnector.Models.csproj;Reqnroll.VisualStudio.ItemTemplates/Reqnroll.VisualStudio.ItemTemplates.csproj;Reqnroll.VisualStudio.Package/Reqnroll.VisualStudio.Package.csproj`, last commit 2026-05-21T14:48:38
- `Roopesh519/Cucumber-Assessment` — 3 features, 35 scenarios, licence `isc`, build `package.json`, last commit 2024-07-06T18:04:46
- `LeeShyanYeong/SpecWarden` — 4 features, 64 scenarios, licence `mit`, build `src/backend/StickyNotes.Api/StickyNotes.Api.csproj;src/backend/StickyNotes.Tests/StickyNotes.Tests.csproj;src/frontend/package.json;tests/acceptance/playwright/package.json`, last commit 2026-06-22T11:15:04
- `reportportal/agent-java-cucumber6` — 27 features, 41 scenarios, licence `mit`, build `build.gradle;gradlew`, last commit 2026-04-08T19:19:47
- `znsio/teswiz` — 29 features, 88 scenarios, licence `mit`, build `build.gradle;gradlew;package.json`, last commit 2026-10-17T09:29:39
- `reportportal/agent-java-cucumber` — 22 features, 34 scenarios, licence `mit`, build `build.gradle;gradlew`, last commit 2025-06-17T13:48:40
- `Karzone/SpecReport` — 11 features, 38 scenarios, licence `mit`, build `samples/CaptureSampleTests/CaptureSampleTests.csproj;samples/FullStackSample/FullStackSample.csproj;samples/SampleTests/SampleTests.csproj;spikes/M1.HttpAttribution/M1.HttpAttribution.csproj`, last commit 2026-07-31T19:31:27
- `fslev/cucumber-jutils` — 16 features, 96 scenarios, licence `mit`, build `pom.xml`, last commit 2026-11-20T20:45:40
- `trivago/cucable-plugin` — 21 features, 29 scenarios, licence `mit`, build `example-project/pom.xml;plugin-code/mvnw;plugin-code/pom.xml`, last commit 2026-07-27T16:06:10

_Per-repo detail: `data/pilot/screen.csv`._
