export interface Item { price: number; qty: number }
export interface Invoice { subtotal: number; tax: number; total: number }

// All arithmetic is done in integer cents and integer basis points (1/100 of a
// percent). Doubles are only used at the edges, to read and to present values.
function toCents(dollars: number): number {
  // A price such as 1.005 has no exact number of cents: refuse it rather than pick one quietly.
  if (Number(dollars.toFixed(2)) !== dollars) throw new RangeError("price must have at most two decimal places");
  return exact(Math.round(dollars * 100));
}

// Integer arithmetic is exact only up to 2^53; past it a cent can vanish without any error.
function exact(cents: number): number {
  if (!Number.isSafeInteger(cents)) throw new RangeError("amount too large to count exactly in cents");
  return cents;
}
const fromCents = (cents: number): number => cents / 100;

export function invoiceTotal(items: Item[], taxRate: number): Invoice {
  if (!(taxRate >= 0 && taxRate <= 1)) throw new RangeError("tax rate must be a fraction between 0 and 1");
  for (const it of items) {
    if (!Number.isInteger(it.qty) || it.qty < 1) throw new RangeError("qty must be a positive integer");
    if (!Number.isFinite(it.price) || it.price < 0) throw new RangeError("price must be a non-negative number of dollars");
  }
  const subtotal = items.reduce((sum, it) => exact(sum + toCents(it.price) * it.qty), 0);
  const bps = Math.round(taxRate * 10000);
  if (Math.abs(taxRate * 10000 - bps) > 1e-6) throw new RangeError("tax rate must be a whole number of basis points (0.0001)");
  const tax = Math.floor(exact(subtotal * bps + 5000) / 10000); // half a cent rounds up
  return { subtotal: fromCents(subtotal), tax: fromCents(tax), total: fromCents(subtotal + tax) };
}
