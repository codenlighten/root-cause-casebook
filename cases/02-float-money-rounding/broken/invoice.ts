export interface Item { price: number; qty: number }
export interface Invoice { subtotal: number; tax: number; total: number }

const round2 = (x: number): number => Math.round(x * 100) / 100;

export function invoiceTotal(items: Item[], taxRate: number): Invoice {
  for (const it of items) {
    if (!Number.isInteger(it.qty) || it.qty < 1) throw new RangeError("qty must be a positive integer");
  }
  const subtotal = items.reduce((sum, it) => sum + it.price * it.qty, 0);
  const tax = round2(subtotal * taxRate);
  return { subtotal, tax, total: round2(subtotal + tax) };
}
