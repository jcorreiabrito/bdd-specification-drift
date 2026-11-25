// DELIBERATELY UNEXERCISED DOMAIN MODULE — NO_COVERAGE control.
//
// Nothing in this project imports this file. It exists so that a mutation run reports a
// non-zero NO_COVERAGE count, which is the only way to demonstrate empirically that the
// tool distinguishes "executed and survived" from "never executed". Without such a module
// a run can report NO_COVERAGE = 0 simply because the suite happens to cover everything,
// and that zero proves nothing about the harness.
//
// It is written as plausible business logic (loyalty tiers) so it is indistinguishable
// from real domain code to the mutation operator set.

export function loyaltyDiscount(years, spend) {
  if (years >= 5 && spend > 10000) {
    return 0.20;
  }
  if (years >= 2 && spend > 5000) {
    return 0.10;
  }
  if (years >= 1) {
    return 0.05;
  }
  return 0;
}

export function loyaltyTier(years, spend) {
  const rate = loyaltyDiscount(years, spend);
  if (rate >= 0.20) return 'platinum';
  if (rate >= 0.10) return 'gold';
  if (rate > 0) return 'silver';
  return 'bronze';
}

export function qualifiesForBonus(years, spend) {
  return years > 3 || spend > 7500;
}
