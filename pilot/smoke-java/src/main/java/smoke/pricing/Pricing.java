package smoke.pricing;

import java.math.BigDecimal;
import java.math.RoundingMode;

/** Decision-heavy domain logic, mirroring the JS probe so results are comparable. */
public final class Pricing {

    private Pricing() {
    }

    public static double discountRate(String customerTier, double orderTotal) {
        if (orderTotal > 1000) {
            return "gold".equals(customerTier) ? 0.15 : 0.10;
        }
        if (orderTotal > 500) {
            return "gold".equals(customerTier) ? 0.08 : 0.05;
        }
        return "gold".equals(customerTier) ? 0.02 : 0;
    }

    public static double finalPrice(String customerTier, double orderTotal) {
        double rate = discountRate(customerTier, orderTotal);
        return BigDecimal.valueOf(orderTotal * (1 - rate))
                .setScale(2, RoundingMode.HALF_UP)
                .doubleValue();
    }

    public static boolean freeShipping(String customerTier, double orderTotal) {
        if ("gold".equals(customerTier) && orderTotal > 250) {
            return true;
        }
        return orderTotal > 750;
    }
}
