"""Canonical differential-kill metrics for the BDD specification-drift study.

WHY THIS MODULE EXISTS
----------------------
An earlier version of this analysis defined

    DK_norm = MS_cov(FULL, S) - MS_cov(BDD, S)

and described it in the manuscript as *"what the specification layer adds beyond the
repository's other tests"*. That is mathematically inverted. Consider the two
configurations:

    decorative BDD :  K_BDD = {}          K_NON_BDD = 90%   ->  DK_norm = +0.90
    valuable BDD   :  K_BDD = 80%         K_NON_BDD = 50%   ->  DK_norm = +0.00

The metric reports a large positive number precisely when BDD contributes nothing, and
reports zero when BDD contributes the 30 percentage points that only it detects. The
quantity it actually measured is the uplift of the *non-BDD* tests.

THE CORRECTED MODEL
-------------------
Three execution modes over one mutant set M:

    BDD      : the Cucumber/Gherkin scenarios only
    NON_BDD  : all other tests (unit/integration), excluding Cucumber runners
    FULL     : BDD union NON_BDD

Coverage containment is an invariant, not an assumption to be hoped for:

    executed(BDD)     subset-of executed(FULL)
    executed(NON_BDD) subset-of executed(FULL)

The comparison set

    S = executed(BDD) INTERSECT executed(NON_BDD)

is the largest set on which all three modes are *simultaneously* defined and on which
`FULL` kill is honestly decomposable as the union of the other two. Restricting to the
intersection is what makes the algebraic identity below exact rather than approximate.

Metrics (all on S):

    DK_bdd_uplift     = MS_cov(FULL,S) - MS_cov(NON_BDD,S) = |K_BDD \\ K_NON_BDD| / |S|
    DK_nonbdd_uplift  = MS_cov(FULL,S) - MS_cov(BDD,S)     = |K_NON_BDD \\ K_BDD| / |S|
    Overlap           = |K_BDD INTERSECT K_NON_BDD| / |K_FULL|
    BDD_unique_share  = |K_BDD \\ K_NON_BDD| / |K_FULL|
    BDD_total_share   = |K_BDD| / |K_FULL|

`DK_bdd_uplift` is the headline: it is the fraction of S that ONLY the specification
layer kills. `BDD_total_share` counts kills BDD shares with other tests and must never be
reported without `BDD_unique_share` beside it, because a suite that merely repeats what
unit tests already prove can have a total share of 1.0 and a unique share of 0.0.

Degenerate cases return None, never 0. That matters: a repository where nothing is killed
has an *undefined* share, not a zero one, and reporting 0 there would be a fabricated
measurement.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable, Mapping

# Normalised per-mutant statuses (see docs/method.md section 7.1).
KILLED = "KILLED"
SURVIVED = "SURVIVED"
NO_COVERAGE = "NO_COVERAGE"
TIMEOUT = "TIMEOUT"
INVALID = "INVALID"

DETECTED = frozenset({KILLED, TIMEOUT})
NOT_EXECUTED = frozenset({NO_COVERAGE})
EXCLUDED = frozenset({INVALID})


def _killed(statuses: Mapping[str, str], ids: Iterable[str]) -> set[str]:
    """Mutant ids in `ids` whose status counts as detected."""
    return {m for m in ids if statuses.get(m) in DETECTED}


def _executed(statuses: Mapping[str, str]) -> set[str]:
    """Mutants the run actually executed (everything except uncovered/invalid)."""
    return {m for m, s in statuses.items() if s not in NOT_EXECUTED | EXCLUDED}


@dataclass(frozen=True)
class Differential:
    """All differential-kill quantities for one repository on one comparison set S."""

    n_bdd: int
    n_nonbdd: int
    n_full: int
    s_size: int
    killed_bdd: int
    killed_nonbdd: int
    killed_full: int
    killed_bdd_only: int          # |K_BDD \ K_NON_BDD|
    killed_nonbdd_only: int       # |K_NON_BDD \ K_BDD|
    killed_both: int              # |K_BDD & K_NON_BDD|

    ms_cov_bdd: float | None
    ms_cov_nonbdd: float | None
    ms_cov_full: float | None
    dk_bdd_uplift: float | None
    dk_nonbdd_uplift: float | None
    overlap: float | None
    bdd_unique_share: float | None
    bdd_total_share: float | None

    containment_ok: bool
    mode_integrity_ok: bool
    note: str

    def as_dict(self) -> dict:
        return asdict(self)


def _ratio(num: float, den: float) -> float | None:
    return (num / den) if den else None


def compute_differential(
    bdd: Mapping[str, str],
    nonbdd: Mapping[str, str],
    full: Mapping[str, str] | None = None,
) -> Differential:
    """Compute the differential-kill metrics.

    Parameters
    ----------
    bdd, nonbdd, full
        Maps mutant_id -> normalised status. `full` may be omitted when the three-mode
        run is unavailable; the S-based uplifts are still exact as long as FULL is
        modelled as the union of BDD and NON_BDD, which is what `full=None` asserts.

    The comparison set S is ``executed(BDD) & executed(NON_BDD)``. Mutants the BDD run
    covers but the non-BDD run does not (or vice versa) are outside S and are reported
    only through the counts, never silently folded into a score.
    """
    exec_bdd = _executed(bdd)
    exec_nonbdd = _executed(nonbdd)

    if full is None:
        exec_full = exec_bdd | exec_nonbdd
        containment_ok = True
        # With no explicit FULL run we can only assert that the union model holds.
        mode_integrity_ok = True
        full_kills = _killed(bdd, exec_bdd) | _killed(nonbdd, exec_nonbdd)
    else:
        exec_full = _executed(full)
        containment_ok = exec_bdd.issubset(exec_full) and exec_nonbdd.issubset(exec_full)
        full_kills = _killed(full, exec_full)
        # FULL must not kill anything the other two modes jointly miss; if it does, the
        # three-mode run is inconsistent and any decomposition would be an artefact.
        mode_integrity_ok = full_kills.issubset(
            _killed(bdd, exec_bdd) | _killed(nonbdd, exec_nonbdd)
        )

    s = exec_bdd & exec_nonbdd
    k_bdd = _killed(bdd, s)
    k_nonbdd = _killed(nonbdd, s)
    k_full = (full_kills & s) if full is not None else (k_bdd | k_nonbdd)

    only_bdd = k_bdd - k_nonbdd
    only_nonbdd = k_nonbdd - k_bdd
    both = k_bdd & k_nonbdd

    n = len(s)
    ms_bdd = _ratio(len(k_bdd), n)
    ms_nonbdd = _ratio(len(k_nonbdd), n)
    ms_full = _ratio(len(k_full), n)

    # Identity check: MS_full - MS_nonbdd == |K_BDD \ K_NON_BDD| / |S|.
    # Computed directly from set differences so the reported value cannot drift from
    # the set-theoretic definition even if the scores are rounded downstream.
    dk_bdd_uplift = _ratio(len(only_bdd), n) if n else None
    dk_nonbdd_uplift = _ratio(len(only_nonbdd), n) if n else None

    n_full_kills = len(k_full)
    notes = []
    if n == 0:
        notes.append("S empty: no mutant executed by both BDD and NON_BDD runs")
    if not containment_ok:
        notes.append("containment violated: a mode executed mutants outside FULL")
    if not mode_integrity_ok:
        notes.append("FULL killed mutants that neither BDD nor NON_BDD killed")

    return Differential(
        n_bdd=len(bdd),
        n_nonbdd=len(nonbdd),
        n_full=len(full) if full is not None else 0,
        s_size=n,
        killed_bdd=len(k_bdd),
        killed_nonbdd=len(k_nonbdd),
        killed_full=len(k_full),
        killed_bdd_only=len(only_bdd),
        killed_nonbdd_only=len(only_nonbdd),
        killed_both=len(both),
        ms_cov_bdd=ms_bdd,
        ms_cov_nonbdd=ms_nonbdd,
        ms_cov_full=ms_full,
        dk_bdd_uplift=dk_bdd_uplift,
        dk_nonbdd_uplift=dk_nonbdd_uplift,
        overlap=_ratio(len(both), n_full_kills),
        bdd_unique_share=_ratio(len(only_bdd), n_full_kills),
        bdd_total_share=_ratio(len(k_bdd), n_full_kills),
        containment_ok=containment_ok,
        mode_integrity_ok=mode_integrity_ok,
        note="; ".join(notes),
    )


# ---------------------------------------------------------------------------
# Self-tests. Runnable without pytest:  python pipelines/analysis/differential.py
# ---------------------------------------------------------------------------

def _mk(spec: str, n: int) -> dict[str, str]:
    """Build a status map from a compact spec.

    spec is a string of n characters:
        K = killed, S = survived, N = no coverage
    """
    chars = spec.replace(" ", "")
    assert len(chars) == n, f"spec length {len(chars)} != n {n}"
    mapping = {"K": KILLED, "S": SURVIVED, "N": NO_COVERAGE}
    return {f"m{i}": mapping[c] for i, c in enumerate(chars)}


def _run_self_tests() -> int:
    failures = 0

    def check(name: str, got, want, tol=1e-9):
        nonlocal failures
        ok = (got is None and want is None) or (
            want is not None and got is not None and abs(got - want) <= tol
        )
        status = "ok  " if ok else "FAIL"
        print(f"  [{status}] {name}: got={got!r} want={want!r}")
        if not ok:
            failures += 1

    print("case (a) decorative BDD: K_bdd={} , K_nonbdd=90%")
    bdd = _mk("S" * 100, 100)                    # nothing killed
    nonbdd = _mk("K" * 90 + "S" * 10, 100)       # 90% killed
    r = compute_differential(bdd, nonbdd)
    check("S size", r.s_size, 100)
    check("MS_cov(BDD)", r.ms_cov_bdd, 0.0)
    check("MS_cov(NON_BDD)", r.ms_cov_nonbdd, 0.90)
    check("DK_bdd_uplift (must be 0)", r.dk_bdd_uplift, 0.0)
    check("DK_nonbdd_uplift (must be 0.90)", r.dk_nonbdd_uplift, 0.90)
    check("BDD_unique_share (must be 0)", r.bdd_unique_share, 0.0)
    check("BDD_total_share", r.bdd_total_share, 0.0)
    check("Overlap", r.overlap, 0.0)
    # The old, inverted metric would have returned +0.90 here.
    check("old DK_norm would have been 0.90", (r.ms_cov_full - r.ms_cov_bdd), 0.90)

    print("case (b) fully redundant BDD: K_bdd == K_nonbdd == 90%")
    bdd = _mk("K" * 90 + "S" * 10, 100)
    nonbdd = _mk("K" * 90 + "S" * 10, 100)
    r = compute_differential(bdd, nonbdd)
    check("DK_bdd_uplift", r.dk_bdd_uplift, 0.0)
    check("DK_nonbdd_uplift", r.dk_nonbdd_uplift, 0.0)
    check("Overlap (must be 1.0)", r.overlap, 1.0)
    check("BDD_unique_share (must be 0)", r.bdd_unique_share, 0.0)
    check("BDD_total_share (must be 1.0)", r.bdd_total_share, 1.0)

    print("case (c) uniquely valuable BDD: K_nonbdd=50% subset of K_bdd=80%")
    bdd = _mk("K" * 80 + "S" * 20, 100)
    nonbdd = _mk("K" * 50 + "S" * 50, 100)   # kills 0..49, subset of BDD's 0..79
    r = compute_differential(bdd, nonbdd)
    check("killed_bdd_only", r.killed_bdd_only, 30)
    check("killed_nonbdd_only", r.killed_nonbdd_only, 0)
    check("DK_bdd_uplift (must be 0.30)", r.dk_bdd_uplift, 0.30)
    check("DK_nonbdd_uplift (must be 0)", r.dk_nonbdd_uplift, 0.0)
    check("BDD_unique_share (30/80)", r.bdd_unique_share, 30 / 80)
    check("BDD_total_share (80/80)", r.bdd_total_share, 1.0)
    # The old metric returned 0.00 here, erasing BDD's unique contribution.
    check("old DK_norm would have been 0.00", (r.ms_cov_full - r.ms_cov_bdd), 0.0)

    print("case (d) BDD-only repository: K_nonbdd={}")
    bdd = _mk("K" * 60 + "S" * 40, 100)
    nonbdd = _mk("S" * 100, 100)
    r = compute_differential(bdd, nonbdd)
    check("DK_bdd_uplift (must be 0.60)", r.dk_bdd_uplift, 0.60)
    check("DK_nonbdd_uplift (must be 0)", r.dk_nonbdd_uplift, 0.0)
    check("Overlap (no overlapping kills)", r.overlap, 0.0)
    check("BDD_unique_share (must be 1.0)", r.bdd_unique_share, 1.0)
    check("BDD_total_share (must be 1.0)", r.bdd_total_share, 1.0)

    print("case (e) degenerate: no kills at all -> shares undefined, not zero")
    bdd = _mk("S" * 100, 100)
    nonbdd = _mk("S" * 100, 100)
    r = compute_differential(bdd, nonbdd)
    check("BDD_total_share", r.bdd_total_share, None)
    check("Overlap", r.overlap, None)
    check("BDD_unique_share", r.bdd_unique_share, None)

    print("case (f) empty S: BDD covers only m0..m9, NON_BDD only m10..m19")
    bdd = {f"m{i}": (KILLED if i < 5 else SURVIVED) for i in range(10)}
    nonbdd = {f"m{i}": (KILLED if i < 10 else SURVIVED) for i in range(10, 20)}
    r = compute_differential(bdd, nonbdd)
    check("S size", r.s_size, 0)
    check("DK_bdd_uplift", r.dk_bdd_uplift, None)

    print("case (g) three-mode with explicit FULL, consistent")
    bdd = _mk("K" * 30 + "S" * 70, 100)      # kills m0..m29
    nonbdd = _mk("K" * 10 + "S" * 90, 100)   # kills m0..m9 (subset of BDD's kills)
    # FULL must be the union of the two modes; build it from the statuses themselves
    # rather than from a sorted id list (lexicographic order is not numeric order).
    full = {
        m: (KILLED if (bdd.get(m) in DETECTED or nonbdd.get(m) in DETECTED) else SURVIVED)
        for m in bdd
    }
    r = compute_differential(bdd, nonbdd, full)
    check("containment_ok", int(r.containment_ok), 1)
    check("mode_integrity_ok", int(r.mode_integrity_ok), 1)
    # BDD kills 30, NON_BDD kills 10 and all of those are also killed by BDD, so the
    # unique contribution of the specification layer is 30 - 10 = 20 mutants.
    check("killed_bdd_only", r.killed_bdd_only, 20)
    check("DK_bdd_uplift (20 unique / 100)", r.dk_bdd_uplift, 0.20)
    check("DK_nonbdd_uplift (0 unique / 100)", r.dk_nonbdd_uplift, 0.0)

    print("case (h) three-mode inconsistent: FULL kills a mutant neither mode killed")
    bdd = _mk("S" * 100, 100)
    nonbdd = _mk("S" * 100, 100)
    full = _mk("K" * 100, 100)
    r = compute_differential(bdd, nonbdd, full)
    check("mode_integrity_ok (must be 0)", int(r.mode_integrity_ok), 0)

    print()
    if failures:
        print(f"SELF-TESTS FAILED: {failures} failure(s)")
        return 1
    print("SELF-TESTS PASSED: all differential-kill identities hold")
    return 0


if __name__ == "__main__":
    raise SystemExit(_run_self_tests())
