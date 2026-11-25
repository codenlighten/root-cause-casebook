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
