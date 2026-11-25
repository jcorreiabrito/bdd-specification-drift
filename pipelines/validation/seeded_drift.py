#!/usr/bin/env python
"""Seeded-drift validation campaign.

Purpose: establish that the drift indicators respond to *known* drift. Without this, the
indicators are heuristics whose sensitivity is unknown, and an association between an
indicator and a mutation score cannot be interpreted.

Method: take the working JS feasibility suite, inject one controlled drift mutation at a
time, and after each injection re-run (a) the static indicator extractor and (b) the
BDD-only mutation analysis. Then revert. The suite is version-controlled, so `git checkout`
guarantees the baseline is exactly restored between injections — a partially reverted tree
would silently corrupt every subsequent measurement.

Injections (each is a plausible way a real suite rots):

    I1  skip tags            add @wip to two scenarios          -> D1 up
    I2  weakened assertion   compare the value to itself        -> D2 up (W5)
    I3  duplicated scenario  copy an existing scenario           -> D4 up
    I4  mirror step          compute the expected value from
                             the production code being tested   -> D7 up (and D2, D6)
    I5  hardcoded expected   replace a literal with a magic value-> D6 up
    C1  NEGATIVE CONTROL     reformat / add comments only        -> nothing should move

`C1` is not decoration. Without it an indicator that returns "yes, drift" for every input
would score 100% sensitivity and look perfect while being useless.

Outputs:
    data/metrics/seeded_drift.json     baseline + per-injection indicator and score deltas
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
JS = os.path.join(ROOT, "pilot", "smoke-js")
FEATURE = os.path.join(JS, "features", "pricing.feature")
STEPS = os.path.join(JS, "features", "steps.js")
OUT = os.path.join(ROOT, "data", "metrics", "seeded_drift.json")
REPORT = os.path.join(JS, "reports", "mutation.bdd.json")

sys.path.insert(0, os.path.join(ROOT, "pipelines", "metrics"))
import static_metrics as sm  # noqa: E402

INDICATORS = ["D1_skip_ratio", "D2_assertion_weakness_ratio", "D4_redundancy_cluster_ratio",
              "D5_glue_duplication_ratio", "D6_literal_bearing_stepdef_ratio",
              "D7_mirror_stepdef_ratio"]


def read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def revert() -> None:
    subprocess.run(["git", "checkout", "--", "pilot/smoke-js/features/pricing.feature",
                    "pilot/smoke-js/features/steps.js", "pilot/smoke-js/src/pricing.js"],
                   cwd=ROOT, check=False, capture_output=True, text=True)


def static_indicators() -> dict:
    row, _ = sm.compute("feasibility-js", JS)
    return {k: row.get(k) for k in INDICATORS}


def mutation_bdd() -> dict:
    env = dict(os.environ)
    env["npm_config_cache"] = os.path.join(ROOT, ".npm-cache")
    if os.path.exists(REPORT):
        os.remove(REPORT)
    subprocess.run(["npx.cmd", "--no-install", "stryker", "run", "stryker.bdd.json"],
                   cwd=JS, capture_output=True, text=True, encoding="utf-8",
                   errors="replace", env=env, timeout=900)
    if not os.path.exists(REPORT):
        return {"error": "no mutation report produced"}
    data = json.load(open(REPORT, encoding="utf-8"))
    st: dict[str, int] = {}
    for _f, fobj in (data.get("files") or {}).items():
        for m in fobj.get("mutants", []):
            st[m.get("status")] = st.get(m.get("status"), 0) + 1
    killed = st.get("Killed", 0)
    survived = st.get("Survived", 0)
    nocov = st.get("NoCoverage", 0)
    den_all = killed + survived + nocov
    den_cov = killed + survived
    return {
        "mutants": den_all,
        "killed": killed,
        "survived": survived,
        "no_coverage": nocov,
        "MS_all": round(killed / den_all, 4) if den_all else None,
        "MS_cov": round(killed / den_cov, 4) if den_cov else None,
        "status_counts": st,
    }


# ------------------------------------------------------------------ injections

def suite_ok() -> tuple[bool, str]:
    """Run the unmutated Cucumber suite. An injection that breaks the suite is invalid.

    This guard matters: without it, an injection that simply makes the suite fail looks
    like "the indicator did not move", which would be read as indicator insensitivity when
    in fact the experiment was malformed.
    """
    env = dict(os.environ)
    env["npm_config_cache"] = os.path.join(ROOT, ".npm-cache")
    p = subprocess.run(["npx.cmd", "--no-install", "cucumber-js"], cwd=JS,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env, timeout=300)
    tail = (p.stdout or "") + (p.stderr or "")
    return p.returncode == 0, tail.strip().splitlines()[-1][:160] if tail.strip() else ""


def inject_skip() -> str:
    t = read(FEATURE)
    # A tag must occupy its own line; appending it to the scenario text produces invalid
    # Gherkin, which the parser silently ignores, making D1 look insensitive.
    if "\n  @wip\n" in t:
        return "already tagged"
    t2 = t.replace("\n  Scenario:", "\n  @wip\n  Scenario:", 2)
    if t2 == t:
        return "scenario anchor missing"
    write(FEATURE, t2)
    return "ok"


def inject_weaken_assertion() -> str:
    t = read(STEPS)
    old = "assert.equal(finalPrice(tier, total), expected);"
    if old not in t:
        return "assertion anchor missing"
    write(STEPS, t.replace(old, "assert.equal(finalPrice(tier, total), finalPrice(tier, total));", 1))
    return "ok"


def inject_duplicate_scenario() -> str:
    t = read(FEATURE)
    marker = "  Scenario: Standard customer with a small order gets no discount"
    if marker not in t:
        return "scenario anchor missing"
    head, tail = t.split(marker, 1)
    write(FEATURE, t + "\n" + marker + tail.split("  Scenario:")[0])
    return "ok"


def inject_mirror_step() -> str:
    t = read(STEPS)
    old = "  assert.equal(finalPrice(tier, total), expected);"
    if old not in t:
        return "assertion anchor missing"
    # The mirror must re-derive the expected value from the production calculation, so the
    # oracle moves with the mutant. discountRate must be imported for the injection to
    # compile; forgetting that is what made the first attempt invalid rather than
    # informative.
    if "discountRate" not in t.split("\n")[2]:
        t = t.replace("import { finalPrice, freeShipping } from '../src/pricing.js';",
                      "import { finalPrice, freeShipping, discountRate } from '../src/pricing.js';", 1)
    new = ("  // mirror: the expected value is re-derived from the production calculation, so\n"
           "  // the assertion moves with any mutant that changes the calculation itself\n"
           "  assert.equal(finalPrice(tier, total),\n"
           "    Math.round(total * (1 - discountRate(tier, total)) * 100) / 100);")
    write(STEPS, t.replace(old, new, 1))
    return "ok"


def inject_hardcoded() -> str:
    t = read(STEPS)
    old = "assert.equal(finalPrice(tier, total), expected);"
    if old not in t:
        return "assertion anchor missing"
    write(STEPS, t.replace(old, "assert.equal(finalPrice(tier, total), 1700.00);", 1))
    return "ok"


def inject_negative_control() -> str:
    t = read(STEPS)
    write(STEPS, "// Negative control: comments and whitespace only, behaviour unchanged.\n\n" + t)
    s = read(FEATURE)
    write(FEATURE, s.replace("\n\n  Scenario:", "\n\n\n  Scenario:", 1))
    return "ok"


CAMPAIGN = [
    ("I1_skip_tags", inject_skip, "D1_skip_ratio", "up"),
    ("I2_weakened_assertion", inject_weaken_assertion, "D2_assertion_weakness_ratio", "up"),
    ("I3_duplicate_scenario", inject_duplicate_scenario, "D4_redundancy_cluster_ratio", "up"),
    ("I4_mirror_step", inject_mirror_step, "D7_mirror_stepdef_ratio", "up"),
    # D6 is already 1.0 at baseline (every step definition carries a literal), so it has no
    # headroom. This injection therefore tests a ceiling, not a sensitivity.
    ("I5_hardcoded_expected", inject_hardcoded, "D6_literal_bearing_stepdef_ratio", "saturated"),
    ("C1_negative_control", inject_negative_control, None, "unchanged"),
]


def main() -> int:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    revert()
    print("baseline: measuring static indicators and BDD mutation score ...")
    base_static = static_indicators()
    # Determinism check: the extractor must return the same values twice on the same tree.
    # A non-deterministic baseline would make every delta below uninterpretable.
    again = static_indicators()
    if again != base_static:
        print(f"  WARNING: extractor is not deterministic: {base_static} vs {again}")
    base_mut = mutation_bdd()
    print(f"  baseline static: { {k: (round(v,3) if isinstance(v,(int,float)) else v) for k,v in base_static.items()} }")
    print(f"  baseline mutation: MS_cov={base_mut.get('MS_cov')} killed={base_mut.get('killed')} nocov={base_mut.get('no_coverage')}")

    results = []
    for name, fn, target, expect in CAMPAIGN:
        revert()
        msg = fn()
        if msg != "ok":
            results.append({"injection": name, "applied": False, "error": msg})
            print(f"  {name}: SKIPPED ({msg})")
            revert()
            continue
        st = static_indicators()
        deltas = {}
        for ind in INDICATORS:
            b, a = base_static.get(ind), st.get(ind)
            if isinstance(b, (int, float)) and isinstance(a, (int, float)):
                deltas[ind] = round(a - b, 4)
            else:
                deltas[ind] = None

        ok, why = suite_ok()
        if not ok:
            results.append({
                "injection": name, "applied": True, "valid": False,
                "reason": f"injection made the unmutated suite fail: {why}",
                "indicator_deltas": deltas,
            })
            print(f"  {name}: INVALID injection (suite failed: {why})")
            revert()
            continue

        mu = mutation_bdd()
        observed = "unchanged"
        if target and deltas.get(target) is not None:
            d = deltas[target]
            if expect == "saturated" and d == 0 and base_static.get(target) == 1.0:
                observed = "cannot_move_saturated"
            elif d > 0:
                observed = "moved_in_expected_direction"
            elif d < 0:
                observed = "moved_wrong_direction"
            else:
                observed = "no_movement"

        ms_delta = None
        if base_mut.get("MS_cov") is not None and mu.get("MS_cov") is not None:
            ms_delta = round(mu["MS_cov"] - base_mut["MS_cov"], 4)

        results.append({
            "injection": name,
            "applied": True,
            "valid": True,
            "target_indicator": target,
            "expected": expect,
            "observed": observed,
            "indicator_deltas": deltas,
            "mutation": mu,
            "MS_cov_delta": ms_delta,
        })
        print(f"  {name}: {observed}; target delta="
              f"{deltas.get(target) if target else 'n/a'}; MS_cov delta={ms_delta}")
        revert()

    revert()
    valid = [r for r in results if r.get("valid")]
    invalid = [r for r in results if r.get("valid") is False]
    targeted_list = [r for r in valid if r.get("expected") == "up"]
    detected = sum(1 for r in targeted_list
                   if r.get("observed") == "moved_in_expected_direction")
    saturated = [r for r in valid if r.get("expected") == "saturated"]
    control_ok = all(r.get("observed") == "unchanged"
                     for r in valid if r.get("injection", "").startswith("C1"))
    payload = {
        "suite": "feasibility-js",
        "baseline_static": base_static,
        "baseline_mutation": base_mut,
        "results": results,
        "valid_injections": len(valid),
        "invalid_injections": len(invalid),
        "sensitivity_targets": len(targeted_list),
        "detected": detected,
        "detection_rate": round(detected / len(targeted_list), 4) if targeted_list else None,
        "false_negatives": [r["injection"] for r in targeted_list
                            if r.get("observed") != "moved_in_expected_direction"],
        "saturated_indicators": [{"injection": r["injection"],
                                  "indicator": r["target_indicator"],
                                  "baseline_value": base_static.get(r["target_indicator"])}
                                 for r in saturated],
        "negative_control_clean": control_ok,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"\nseeded-drift: {detected}/{len(targeted_list)} sensitivity targets detected; "
          f"{len(invalid)} invalid injections; {len(saturated)} saturated; "
          f"negative control clean={control_ok}")
    print(f"wrote {OUT}")
    ok = (targeted_list and detected == len(targeted_list) and control_ok and not invalid)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
