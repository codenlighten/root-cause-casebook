import { test } from "node:test";
import assert from "node:assert/strict";
import { invoiceTotal } from "./invoice.ts";

test("a half-cent of tax rounds up (6.00 at 7.25% is 0.435, so 0.44)", () => {
  const r = invoiceTotal([{ price: 6.0, qty: 1 }], 0.0725);
  assert.equal(r.tax, 0.44);
  assert.equal(r.total, 6.44);
});

test("subtotal of 0.10 + 0.20 is exactly 0.30", () => {
  const r = invoiceTotal([{ price: 0.1, qty: 1 }, { price: 0.2, qty: 1 }], 0);
  assert.equal(r.subtotal, 0.3);
});

test("rejects a negative quantity with a message that says what to do", () => {
  assert.throws(() => invoiceTotal([{ price: 1, qty: -1 }], 0.1), /qty must be a positive integer/);
});

test("refuses a price with a fraction of a cent instead of rounding it quietly", () => {
  assert.throws(() => invoiceTotal([{ price: 1.005, qty: 1 }], 0), /at most two decimal places/);
});

test("refuses a tax rate that is not a fraction between 0 and 1", () => {
  for (const rate of [NaN, -0.1, 7.25, Infinity]) {
    assert.throws(() => invoiceTotal([{ price: 6, qty: 1 }], rate), /tax rate/, String(rate));
  }
});
