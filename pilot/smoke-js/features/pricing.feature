Feature: Customer pricing
  As a retailer
  I want tiered discounts and shipping thresholds
  So that pricing reflects the business rules

  Scenario: Gold customer with a large order gets 15% off
    Given a gold customer
    When they place an order of 2000
    Then the final price is 1700.00
    And shipping is free

  Scenario: Standard customer with a large order gets 10% off
    Given a standard customer
    When they place an order of 2000
    Then the final price is 1800.00
    And shipping is free

  Scenario: Standard customer with a mid order gets 5% off
    Given a standard customer
    When they place an order of 600
    Then the final price is 570.00
    And shipping is not free

  Scenario: Standard customer with a small order gets no discount
    Given a standard customer
    When they place an order of 100
    Then the final price is 100.00
    And shipping is not free
