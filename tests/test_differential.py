"""Regression tests for the differential-kill metrics.

These exist because the first version of this analysis shipped an *inverted* headline
metric. The tests below are the four configurations that expose the inversion, plus the
degenerate cases where a share is undefined rather than zero. Any future edit that
reintroduces the inversion fails here before it can reach a manuscript.

Run with either:
    python -m unittest discover -s tests -v
    python -m pytest tests -q          # if pytest is available
"""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "pipelines", "analysis"))

from differential import (  # noqa: E402
    KILLED, NO_COVERAGE, SURVIVED, compute_differential,
)


def mk(spec: str) -> dict[str, str]:
    """spec: one char per mutant, K=killed S=survived N=no-coverage."""
    mapping = {"K": KILLED, "S": SURVIVED, "N": NO_COVERAGE}
    return {f"m{i}": mapping[c] for i, c in enumerate(spec)}


class TestDecorativeBDD(unittest.TestCase):
    """BDD kills nothing while the unit tests kill 90%: BDD adds zero."""

    def setUp(self):
        self.r = compute_differential(mk("S" * 100), mk("K" * 90 + "S" * 10))

    def test_bdd_uplift_is_zero(self):
        self.assertEqual(self.r.dk_bdd_uplift, 0.0)

    def test_nonbdd_uplift_carries_everything(self):
        self.assertAlmostEqual(self.r.dk_nonbdd_uplift, 0.90)

    def test_unique_share_is_zero(self):
        self.assertEqual(self.r.bdd_unique_share, 0.0)

    def test_old_inverted_metric_would_have_been_large(self):
        # The inverted definition MS_cov(FULL)-MS_cov(BDD) reports +0.90 here, which is
        # exactly the failure the corrected metric avoids.
        self.assertAlmostEqual(self.r.ms_cov_full - self.r.ms_cov_bdd, 0.90)


class TestFullyRedundantBDD(unittest.TestCase):
    """BDD kills exactly what the unit tests already kill: maximal overlap, zero unique."""

    def setUp(self):
        self.r = compute_differential(mk("K" * 90 + "S" * 10), mk("K" * 90 + "S" * 10))

    def test_both_uplifts_are_zero(self):
        self.assertEqual(self.r.dk_bdd_uplift, 0.0)
        self.assertEqual(self.r.dk_nonbdd_uplift, 0.0)

    def test_overlap_is_one(self):
        self.assertEqual(self.r.overlap, 1.0)

    def test_total_share_is_one_but_unique_share_is_zero(self):
        # This pair is why the manuscript must never report total share alone.
        self.assertEqual(self.r.bdd_total_share, 1.0)
        self.assertEqual(self.r.bdd_unique_share, 0.0)


class TestUniquelyValuableBDD(unittest.TestCase):
    """BDD kills 80%, unit tests 50% and the 50% is a subset of the 80%."""

    def setUp(self):
        self.r = compute_differential(mk("K" * 80 + "S" * 20), mk("K" * 50 + "S" * 50))

    def test_unique_kills_are_30(self):
        self.assertEqual(self.r.killed_bdd_only, 30)

    def test_bdd_uplift_is_030(self):
        self.assertAlmostEqual(self.r.dk_bdd_uplift, 0.30)

    def test_nonbdd_uplift_is_zero(self):
        self.assertEqual(self.r.dk_nonbdd_uplift, 0.0)

    def test_unique_share_is_30_of_80(self):
        self.assertAlmostEqual(self.r.bdd_unique_share, 30 / 80)

    def test_old_inverted_metric_would_have_been_zero(self):
        # The inverted definition erases BDD's unique 30-point contribution entirely.
        self.assertEqual(self.r.ms_cov_full - self.r.ms_cov_bdd, 0.0)


class TestBDDOnlyRepository(unittest.TestCase):
    """A repository with no non-BDD tests: BDD is the whole oracle."""

    def setUp(self):
        self.r = compute_differential(mk("K" * 60 + "S" * 40), mk("S" * 100))

    def test_bdd_uplift_equals_bdd_score(self):
        self.assertAlmostEqual(self.r.dk_bdd_uplift, 0.60)

    def test_nonbdd_uplift_is_zero(self):
        self.assertEqual(self.r.dk_nonbdd_uplift, 0.0)

    def test_shares_are_one(self):
        self.assertEqual(self.r.bdd_unique_share, 1.0)
        self.assertEqual(self.r.bdd_total_share, 1.0)


class TestDegenerateCases(unittest.TestCase):
    """Undefined is not zero: a fabricated 0.0 would be a measurement we did not take."""

    def test_no_kills_yields_none_shares(self):
        r = compute_differential(mk("S" * 10), mk("S" * 10))
        self.assertIsNone(r.bdd_total_share)
        self.assertIsNone(r.bdd_unique_share)
        self.assertIsNone(r.overlap)

    def test_disjoint_coverage_yields_empty_s(self):
        bdd = {f"m{i}": (KILLED if i < 5 else SURVIVED) for i in range(10)}
        nonbdd = {f"m{i}": (KILLED if i < 10 else SURVIVED) for i in range(10, 20)}
        r = compute_differential(bdd, nonbdd)
        self.assertEqual(r.s_size, 0)
        self.assertIsNone(r.dk_bdd_uplift)

    def test_uncovered_mutants_are_excluded_from_s(self):
        # A NO_COVERAGE mutant in the BDD run cannot be in the comparison set.
        r = compute_differential(mk("KN" + "K" * 8), mk("K" * 10))
        self.assertEqual(r.s_size, 9)


class TestThreeModeIntegrity(unittest.TestCase):

    def test_consistent_full_run_passes_integrity(self):
        bdd = mk("K" * 30 + "S" * 70)
        nonbdd = mk("K" * 10 + "S" * 90)
        full = {m: (KILLED if (bdd[m] == KILLED or nonbdd[m] == KILLED) else SURVIVED)
                for m in bdd}
        r = compute_differential(bdd, nonbdd, full)
        self.assertTrue(r.containment_ok)
        self.assertTrue(r.mode_integrity_ok)
        self.assertAlmostEqual(r.dk_bdd_uplift, 0.20)

    def test_full_killing_more_than_union_is_flagged(self):
        r = compute_differential(mk("S" * 10), mk("S" * 10), mk("K" * 10))
        self.assertFalse(r.mode_integrity_ok)

    def test_containment_violation_is_flagged(self):
        bdd = mk("K" * 10)
        nonbdd = mk("K" * 10)
        # FULL omits a mutant the BDD run executed -> containment violated.
        full = {f"m{i}": KILLED for i in range(5)}
        r = compute_differential(bdd, nonbdd, full)
        self.assertFalse(r.containment_ok)


if __name__ == "__main__":
    unittest.main(verbosity=2)
