# 03. Deposits that disappear under load (Go)

> **Constructed example.** This bug was written for this repository to demonstrate a diagnosis method. It is not a report from any client, employer or production system.

## Symptom

"We sometimes record two deposits at almost the same moment and the balance only reflects one. It never happens when I test by hand."

## Reproduce

```bash
./run-case.sh 3
```

This also prints the Go race detector's output for the broken code (the "extra evidence" section).

## Investigation

1. **Find the invariant.** After depositing a and b the balance must be a + b. Checking totals against a ledger showed the shortfall was always exactly one of the two amounts, never a partial value. That points at a lost update, not at arithmetic.
2. **Hypothesis: the arithmetic or integer type is wrong.** Rejected: sequential deposits are always right, and the missing amount is a whole deposit.
3. **Run the race detector.** `go test -race` on a 200-goroutine test reported `WARNING: DATA RACE` with a read at `Deposit` (the read of `balance`) against a previous write at the line that stores it.
4. **Make it deterministic.** A stress test only fails sometimes. Between the read and the write there is a window; the code now calls a no-op hook, `raceWindow`, there, and the test replaces it with a barrier that makes two deposits both read before either writes. Result for the broken code: balance 100 (or 50) after depositing 100 and 50, every run.
5. **Make the test safe for correct code.** With a mutex the second deposit is correctly blocked, so it never reaches the barrier. The barrier gives up after 200 ms, so the test finishes and still passes.

## Root cause

`Deposit` reads the balance, then writes balance + amount later without holding a lock across both steps, so two concurrent deposits both start from the same old balance and the later write overwrites the earlier one.

## Fix

A mutex held across the entire read-modify-write (and in `Balance` for a safe read). Note the comment in the code: locking the read and the write separately would silence the race detector and still lose updates.

## Why the regression test would have caught it

The forced interleaving fails the broken code on every run, with no dependence on scheduler luck, and a correct implementation is never made to fail by it. Deliberate break: taking the lock separately for the read and for the write keeps the race detector quiet but still loses a deposit (balance 50 instead of 150), and the deterministic test fails.

## How to spot this class next time

- A shortfall equal to one whole operation is a lost update. Think read-modify-write.
- "Fine in my test, wrong under load" plus shared mutable state: run the race detector, then write the interleaving as a test.
- A clean race detector does not prove atomicity. Check the whole check-then-act sequence.

## Limits

The test seam (`raceWindow`) is a package variable that tests mutate, so these tests cannot run in parallel with each other. Across processes or database rows, a mutex does not help; that needs a transaction or an atomic update in the store.
