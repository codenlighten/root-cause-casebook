# 04. The last three items never show up (TypeScript)

> **Constructed example.** This bug was written for this repository to demonstrate a diagnosis method. It is not a report from any client, employer or production system.

## Symptom

"I have 23 results, the page says 'Page 1 of 2', and I can never see items 21 to 23."

## Reproduce

```bash
./run-case.sh 4
```

## Investigation

1. **Count what is reachable.** Walking every page and counting items gave 20 for 23 items. The missing items were always the final partial page.
2. **Vary the size of the data.** 20 items: complete. 21 and 23 items: items lost. 19 items showed 1 page. So only a partial last page fails; an exact multiple works.
3. **Hypothesis: the slice window is off by one.** Rejected. `slice(start, start + pageSize)` with `start = (page - 1) * pageSize` returned exactly items 21 to 23 when asked for page 3 directly.
4. **Hypothesis: the UI skips a page.** Rejected: the UI uses the `totalPages` it is given.
5. **Inspect `totalPages`.** It was `Math.floor(23 / 10)`, which is 2. The data was fine; the page count hid page 3.

## Root cause

`totalPages` rounded down instead of up, so a partial last page was not counted and could not be reached.

## Fix

`Math.ceil(all.length / pageSize)`.

## Why the regression test would have caught it

The test uses 23 items (partial last page), 20 items (exact multiple) and 0 items (empty), and checks that walking all pages returns every item exactly once. Deliberate break: `Math.floor(n / size) + 1` is a tempting wrong fix, and it fails the exact-multiple and empty cases (an extra empty page), which a test with only 23 items would miss.

## How to spot this class next time

- Test the boundaries of a range: 0, 1, exactly one page, one over, many.
- Prove "no item lost and none repeated" by walking everything, not by checking page 1.
- Be suspicious of `floor` and `+ 1` where a ceiling is meant.

## Limits

Pages are 1-based and the data is an in-memory array. Offset pagination over data that changes while the user pages can still skip or repeat rows; that needs cursor pagination.
