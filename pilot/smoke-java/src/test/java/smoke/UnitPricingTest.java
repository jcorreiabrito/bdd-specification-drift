package smoke;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import smoke.pricing.Pricing;

/**
 * NON_BDD tests: ordinary JUnit unit tests, deliberately not expressed as Gherkin.
 *
 * <p>These have to be a genuinely different test set from the Cucumber scenarios,
 * otherwise the NON_BDD execution mode would be a copy of the BDD mode and the
 * differential would be meaningless. They therefore probe the boundaries the scenarios do
 * not: the strict inequalities at 500 and 1000, the shipping threshold at exactly 750, and
 * the rounding of the final price.
 */
class UnitPricingTest {

    @Test
    @DisplayName("standard tier earns nothing below the 500 boundary")
    void standardBelow500() {
        assertEquals(0.0, Pricing.discountRate("standard", 499.0), 1e-9);
    }

    @Test
    @DisplayName("the 500 boundary is strictly greater-than")
    void standardAt500() {
        // > 500 is false at exactly 500, so the rate falls through to the final branch.
        assertEquals(0.0, Pricing.discountRate("standard", 500.0), 1e-9);
    }

    @Test
    @DisplayName("standard tier earns 5% just above 500")
    void standardJustAbove500() {
        assertEquals(0.05, Pricing.discountRate("standard", 501.0), 1e-9);
    }

    @Test
    @DisplayName("the 1000 boundary is strictly greater-than")
    void standardAt1000() {
        assertEquals(0.05, Pricing.discountRate("standard", 1000.0), 1e-9);
    }

    @Test
    @DisplayName("standard tier earns 10% just above 1000")
    void standardJustAbove1000() {
        assertEquals(0.10, Pricing.discountRate("standard", 1001.0), 1e-9);
    }

    @Test
    @DisplayName("gold tier earns 2% on small orders")
    void goldSmallOrder() {
        assertEquals(0.02, Pricing.discountRate("gold", 100.0), 1e-9);
    }

    @Test
    @DisplayName("shipping is free at 751 for a standard customer")
    void shippingAbove750() {
        assertTrue(Pricing.freeShipping("standard", 751.0));
    }

    @Test
    @DisplayName("shipping is not free at exactly 750")
    void shippingAt750() {
        assertFalse(Pricing.freeShipping("standard", 750.0));
    }

    @Test
    @DisplayName("final price is rounded to two decimals")
    void finalPriceRounding() {
        assertEquals(949.99, Pricing.finalPrice("standard", 999.99), 1e-9);
    }
}
