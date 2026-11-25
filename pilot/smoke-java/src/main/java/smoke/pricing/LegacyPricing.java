package smoke.pricing;

/**
 * DELIBERATELY UNEXERCISED DOMAIN MODULE — the Java NO_COVERAGE control.
 *
 * <p>Nothing in this project references this class. It exists so that a PIT run reports a
 * non-zero count of mutants with no coverage, which is the only empirical demonstration
 * that the tool separates "executed and survived" from "never executed". Without such a
 * class a run can legitimately report zero uncovered mutants simply because the suite
 * covers everything, and that zero would prove nothing about the harness.
 *
 * <p>It is written as plausible business logic (loyalty tiers) so that, to PIT's operator
 * set, it is indistinguishable from real domain code.
 */
public final class LegacyPricing {

    private LegacyPricing() {
    }

    public static double loyaltyDiscount(int years, double spend) {
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

    public static String loyaltyTier(int years, double spend) {
        double rate = loyaltyDiscount(years, spend);
        if (rate >= 0.20) {
            return "platinum";
        }
        if (rate >= 0.10) {
            return "gold";
        }
        if (rate > 0) {
            return "silver";
        }
        return "bronze";
    }

    public static boolean qualifiesForBonus(int years, double spend) {
        return years > 3 || spend > 7500;
    }
}
