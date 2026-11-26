# Root-cause casebook

[![CI](https://github.com/codenlighten/root-cause-casebook/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/codenlighten/root-cause-casebook/actions/workflows/ci.yml)

Nine small bugs in five languages, each diagnosed from a user-style symptom to a root cause, fixed, and pinned by a minimal regression test. It shows how I find the cause of a bug instead of patching its symptom.

> **Every case is a constructed example.** The bugs were written for this repository to teach and demonstrate a method. None is a real incident, a client report or a production system, and no case describes anyone's actual software.

## Run it

Needs Node 22 or newer, Python 3.10+ (standard library only), Go 1.22+ and a Rust toolchain. Nothing else is installed.

```bash
./run-case.sh 3     # one case: broken fails, fixed passes, partly reverted fix fails again
./run-all.sh        # all nine, summarised as a table (about 15 s once the toolchains are present)
```

Each case lives in `cases/NN-name/` with `README.md` (the write-up), `broken/` and `fixed/` (complete, small projects with an identical test file), `test.sh` (how to run the tests) and `break.patch` (undoes part of the fix on purpose). `run-case.sh` copies each state to a temp directory and never modifies the checkout.

## The cases

| # | Class | Language | Symptom | Root cause |
|---|---|---|---|---|
| [01](cases/01-dst-date-arithmetic) | Time zones / DST | Python | A daily 9:00 reminder fires at 10:00 on the day the clocks change | Added 24 elapsed hours in UTC, not one calendar day in local time |
| [02](cases/02-float-money-rounding) | Floating-point money | TypeScript | Tax is a cent short; a subtotal prints `0.30000000000000004` | Binary floats put half-cent ties just below the tie; money is not computed in integers |
| [03](cases/03-lost-update-race) | Race / lost update | Go | Two near-simultaneous deposits record only one | Read-modify-write with no lock across both steps |
| [04](cases/04-pagination-boundary) | Off-by-one / boundary | TypeScript | The last partial page is unreachable | `totalPages` used `floor` instead of `ceil` |
| [05](cases/05-swallowed-async-error) | Swallowed async error | TypeScript | "3 sent" when one failed; occasional unhandled rejection crash | `forEach(async ...)` never awaits, so `try/catch` sees nothing |
| [06](cases/06-slow-query-n-plus-one) | Slow query: N+1, missing index | SQL (SQLite) | Order history takes about half a second and grows with data | 101 statements per page, each scanning an unindexed table |
| [07](cases/07-integer-overflow-release) | Integer overflow, debug vs release | Rust | A 5,000 MiB upload is recorded as 904 MiB in the shipped build | `u32 * u32` wrapped, then widened to `u64` |
| [08](cases/08-unicode-lookup) | Unicode normalization / case folding | Python | A name pasted from a PDF is "not found" | Compared with `lower()`; composed and decomposed forms differ |
| [09](cases/09-unbounded-cache-leak) | Resource leak: unbounded cache | Python | Memory climbs until a nightly restart | Cache with a size constant but no eviction |

## How I diagnose

1. **Get the symptom in the user's words, then make it fail on demand.** Until it fails in one command, I am guessing.
2. **Shrink it.** Cut the input, the data, or the code (bisect by date, by size or by commit) until the smallest case that still fails is in front of me. Case 02 went from a long invoice to one 6.00 item.
3. **Look at the real values, not the model in my head.** Print the intermediate number, the code points, the query plan, the statement count or the race detector report. The wrong value usually names the cause (case 07: 947,912,704 is 5,242,880,000 mod 2^32).
4. **Write down each hypothesis and test it, including the ones that turn out wrong.** Case 03 rejects "wrong arithmetic", case 09 rejects "leaked file handles" and "uncollected garbage", case 01 rejects "bad time zone data". Rejected hypotheses are findings.
5. **Fix the cause, with the smallest change that removes it.** Then change the test, not the symptom: the regression test must fail on the broken code for the reason in the write-up.
6. **Break the fix on purpose.** Undo part of it and confirm the test fails again. A test that cannot fail proves nothing. Then say how to spot the class sooner next time.

## What this proves

- Each case fails for the stated reason, not for an incidental one: the failing output is shown by `run-case.sh`.
- Each fix passes the same test file that fails on the broken code, and I verified in all nine that undoing part of the fix makes the test fail again (see below).
- The tests are deterministic. The race in case 03 is forced with a barrier instead of hoping the scheduler cooperates, and the performance case asserts statement count and query plan instead of wall-clock time.
- Where I quote a number (cases 06 and 09), the write-up says how it was measured.

### Deliberate breaks (fix partly reverted, test must fail)

| Case | What I reverted | Result |
|---|---|---|
| 01 | Back to the UTC round trip | spring-forward and fall-back tests fail (10:00 and 08:00), ordinary day passes |
| 02 | Tax computed through floats again | the half-cent test fails (0.43, expected 0.44) |
| 03 | Lock the read and the write separately | race detector stays quiet, balance still wrong (50, expected 150), test fails |
| 04 | `floor(n / size) + 1` instead of `ceil` | exact-multiple and empty-list tests fail |
| 05 | Fire-and-forget sends reported as fulfilled | failure list empty, test fails |
| 06 | Drop the `order_items` index, keep the join | query-plan test fails (`SCAN i`) |
| 07 | Multiply in `u32`, then widen | two of three tests fail (wrapped value) |
| 08 | Remove NFC normalization only | decomposed-name test fails, sharp-s test still passes |
| 09 | Remove the eviction loop | size and LRU tests fail |

`./run-all.sh` repeats all of these on every run, so the table above is re-checked, not remembered.

## Independent re-check

On 2026-11-25 the repository was cloned fresh onto a second Linux machine (Python 3.14.4, Node 22.23, Go 1.22.5, Rust 1.98.1, SQLite 3.46.1) and `./run-all.sh` ended with every case behaving as claimed: the broken state fails, the fix passes and the partly reverted fix fails again. That run found one flaw in the casebook itself: case 07 reused another state's build when `CARGO_TARGET_DIR` was set globally, so the fixed copy failed too. Its build directory is now local to each state.

## What a code review found

An independent AI review (2026-11-26) found faults in my own fixes, which is worth showing in a casebook about root causes. Each behaviour fault got a test that failed first:

| Case | What was still wrong in the "fixed" version |
|---|---|
| 02 | A price of 1.005 was still rounded the wrong way, and a tax rate of `NaN` produced `NaN` totals |
| 05 | A sender that threw before returning a promise still stopped the remaining sends |
| 06 | The single-query rewrite used an inner join, so orders without items vanished |
| 08 | The write-up said the test data was written as escapes; it was not |
| 09 | A type hint allowed users that cannot be cache keys |

## Limits

- These are small, self-contained reductions. They show method, not the effort of tracing a bug through a large system, a database in use, or a distributed deployment.
- The investigation narratives are written to be reproducible with the code in each folder; the "user" reports in them are invented.
- Timings in cases 06 and 09 are single-machine, single-process measurements (AMD Ryzen 5 PRO 5650U, Python 3.14.4, SQLite 3.46.1), so treat them as an illustration of the ratio.
- The SQL case runs on SQLite so it works anywhere; PostgreSQL's planner words things differently.
- Developed and run on Linux. CI runs the same `./run-all.sh` (see `.github/workflows/ci.yml`).

## Licence

MIT. See `LICENSE`.
