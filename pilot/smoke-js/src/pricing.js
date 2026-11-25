// Domain logic under test. Deliberately decision-heavy so that mutation
// operators for boundaries, negation, arithmetic and constants all apply.
export function discountRate(customerTier, orderTotal) {
  if (orderTotal > 1000) {
    return customerTier === 'gold' ? 0.15 : 0.10;
  }
  if (orderTotal > 500) {
    return customerTier === 'gold' ? 0.08 : 0.05;
  }
  return customerTier === 'gold' ? 0.02 : 0;
}

export function finalPrice(customerTier, orderTotal) {
  const rate = discountRate(customerTier, orderTotal);
  return Math.round(orderTotal * (1 - rate) * 100) / 100;
}

export function freeShipping(customerTier, orderTotal) {
  if (customerTier === 'gold' && orderTotal > 250) return true;
  return orderTotal > 750;
}
