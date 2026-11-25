// NON-BDD tests for the three-mode differential-kill harness.
//
// These are ordinary unit tests: they exercise the domain module directly and say nothing
// about Gherkin. They exist so that the NON_BDD execution mode has something to run, which
// is what makes it possible to separate "what BDD adds" from "what the rest of the suite
// adds". They deliberately overlap only partially with the Cucumber scenarios: the unit
// tests probe the tier boundary at 500/1000 and the shipping threshold at 750, while the
// scenarios probe end-to-end pricing for two customer tiers.
//
// Run with the Node built-in test runner:  node --test test/

import test from 'node:test';
import assert from 'node:assert/strict';
import { discountRate, freeShipping, finalPrice } from '../src/pricing.js';

test('standard tier earns no discount below 500', () => {
  assert.equal(discountRate('standard', 499), 0);
});

test('standard tier earns 5% just above 500', () => {
  assert.equal(discountRate('standard', 501), 0.05);
});

// The boundary is strictly greater-than: at exactly 500 the tiered branch does not fire
// and the rate falls through to zero. This is the boundary the Gherkin scenarios do not
// probe, which is why the BDD-only run leaves boundary mutants alive while these unit
// tests kill them -- exactly the kind of unique uplift the three-mode comparison measures.
test('standard tier earns no discount at exactly 500', () => {
  assert.equal(discountRate('standard', 500), 0);
});

test('standard tier earns 10% above 1000', () => {
  assert.equal(discountRate('standard', 1001), 0.10);
});

test('gold tier earns 2% on small orders', () => {
  assert.equal(discountRate('gold', 100), 0.02);
});

test('shipping is free above 750 regardless of tier', () => {
  assert.equal(freeShipping('standard', 751), true);
});

test('shipping is not free at 750 for a standard customer', () => {
  assert.equal(freeShipping('standard', 750), false);
});

test('final price rounds to two decimals', () => {
  assert.equal(finalPrice('standard', 999.99), 949.99);
});
