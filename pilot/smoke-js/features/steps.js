import { Given, When, Then } from '@cucumber/cucumber';
import assert from 'node:assert/strict';
import { finalPrice, freeShipping } from '../src/pricing.js';

let tier;
let total;

Given('a gold customer', function () {
  tier = 'gold';
});

Given('a standard customer', function () {
  tier = 'standard';
});

When('they place an order of {int}', function (amount) {
  total = amount;
});

Then('the final price is {float}', function (expected) {
  assert.equal(finalPrice(tier, total), expected);
});

Then('shipping is free', function () {
  assert.equal(freeShipping(tier, total), true);
});

Then('shipping is not free', function () {
  assert.equal(freeShipping(tier, total), false);
});
