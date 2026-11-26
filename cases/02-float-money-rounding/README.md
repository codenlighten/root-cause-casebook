# 02. Tax that is a cent short (TypeScript)

> **Constructed example.** This bug was written for this repository to demonstrate a diagnosis method. It is not a report from any client, employer or production system.

## Symptom

"The invoice for a 6.00 item at 7.25% tax shows 0.43 tax. Our accountant's spreadsheet says 0.44, and the preview page once showed a subtotal of 0.30000000000000004."

## Reproduce

```bash
./run-case.sh 2
```

## Investigation

1. **Reduce the invoice.** Starting from a long invoice, removing lines until the discrepancy remained left one item: price 6.00, rate 7.25%.
2. **Do the arithmetic by hand.** 6.00 x 0.0725 = 0.435 exactly, a half-cent tie, which must round up to 0.44 under the stated rule.
3. **Instrument.** In Node, `6 * 0.0725` is `0.43499999999999994`, and times 100 is `43.49999999999999`. The double nearest to the decimal 0.0725 is slightly low, so `Math.round` goes down.
4. **Hypothesis: `Math.round` has a rounding bug.** Rejected. It rounds the value it is given correctly; the value it is given is already wrong in the 17th digit.
5. **Search for other ties.** A short brute-force over subtotals and common rates found many ties that round wrongly (for example 2.00 at 7.25%, 2.80 at 8.75%, 11.60 at 8.75%), so this is the whole class and not one data point.
6. **Second symptom, same cause.** `0.1 + 0.2` accumulates in binary, so the unrounded subtotal printed `0.30000000000000004`.

## Root cause

Money was computed with binary floating point, which cannot represent most decimal fractions, so exact half-cent ties landed just below the tie and rounded the wrong way.

## Fix

Convert to integer cents and basis points on entry, do all arithmetic in integers (tax = `floor((cents * bps + 5000) / 10000)`), and divide by 100 only for presentation. Quantity, price and tax rate are validated at the boundary with messages that say what is wrong. A price with a fraction of a cent (1.005) is refused: its double is slightly below the written value, so converting it would round the wrong way, which is this same bug at the front door. For the same reason a rate finer than a basis point is refused, and so is any amount past 2^53 cents, where integer arithmetic stops being exact.

## Why the regression test would have caught it

It contains the exact tie (6.00 at 7.25%) and the 0.10 + 0.20 subtotal. A test using "nice" numbers such as 10.00 at 10% passes on the broken code. Deliberate break: replacing the integer tax line with `Math.round((subtotal / 100) * taxRate * 100)` made the tie test fail (0.43 instead of 0.44).

## How to spot this class next time

- Any money value that goes through `*`, `/` or `Math.round` on a double is suspect.
- Look for results that are off by one unit in the last place, and for half-way cases: that is where float error flips the answer.
- Store and compute money in the smallest unit as an integer, and state the rounding rule in the code.

## Limits

Presentation still returns doubles (cents / 100), which is fine for display but not for further arithmetic. A real system would keep cents or a decimal type all the way to the database.
