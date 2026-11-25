import { test } from "node:test";
import assert from "node:assert/strict";
import { paginate } from "./paginate.ts";

const items = (n: number): number[] => Array.from({ length: n }, (_, i) => i + 1);

test("23 items in pages of 10: three pages, and the last one holds 21..23", () => {
  const first = paginate(items(23), 1, 10);
  assert.equal(first.totalPages, 3);
  assert.deepEqual(paginate(items(23), 3, 10).items, [21, 22, 23]);
});

test("an exact multiple does not produce an empty extra page", () => {
  assert.equal(paginate(items(20), 1, 10).totalPages, 2);
});

test("no items means zero pages and an empty first page", () => {
  const r = paginate([], 1, 10);
  assert.equal(r.totalPages, 0);
  assert.deepEqual(r.items, []);
});

test("every item appears exactly once when walking all pages", () => {
  const all = items(23);
  const { totalPages } = paginate(all, 1, 10);
  const seen = Array.from({ length: totalPages }, (_, i) => paginate(all, i + 1, 10).items).flat();
  assert.deepEqual(seen, all);
});

test("rejects page 0 and a non-integer page size", () => {
  assert.throws(() => paginate([1], 0, 10), /page must be an integer >= 1/);
  assert.throws(() => paginate([1], 1, 2.5), /pageSize must be an integer >= 1/);
});
