package smoke.steps;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import smoke.pricing.Pricing;

public class PricingSteps {

    private String tier;
    private double total;

    @Given("a gold customer")
    public void aGoldCustomer() {
        tier = "gold";
    }

    @Given("a standard customer")
    public void aStandardCustomer() {
        tier = "standard";
    }

    @When("they place an order of {double}")
    public void theyPlaceAnOrderOf(double amount) {
        total = amount;
    }

    @Then("the final price is {double}")
    public void theFinalPriceIs(double expected) {
        assertEquals(expected, Pricing.finalPrice(tier, total), 0.001);
    }

    @Then("shipping is free")
    public void shippingIsFree() {
        assertEquals(true, Pricing.freeShipping(tier, total));
    }

    @Then("shipping is not free")
    public void shippingIsNotFree() {
        assertEquals(false, Pricing.freeShipping(tier, total));
    }
}
