# 07. A 5,000 MiB upload recorded as 904 MiB (Rust)

> **Constructed example.** This bug was written for this repository to demonstrate a diagnosis method. It is not a report from any client, employer or production system.

## Symptom

"Large uploads show the wrong size in the dashboard, only in the deployed build. A 5,000 MiB upload is recorded as about 904 MiB. In development everything looks fine, or it crashes."

## Reproduce

```bash
./run-case.sh 7
```

The test runs in the release profile, because that is the build that ships. The "extra evidence" section runs the same test in a debug build.

## Investigation

1. **Compare builds.** The wrong number appeared in release builds only. In a debug build the same input panics: `attempt to multiply with overflow`. Two different behaviours for one input is the signature of integer overflow: debug builds check, release builds wrap (unless `overflow-checks` is enabled).
2. **Check the number.** The wrong value was 947,912,704. `5,242,880,000 mod 2^32` is 947,912,704. The result had been reduced modulo 2^32, so some 32-bit arithmetic was involved.
3. **Hypothesis: the stored column is too small.** Rejected. The function returns a `u64`, and the value was already wrong when it left the function.
4. **Read the expression.** `(chunks * chunk_size) as u64`: both operands are `u32`, so the multiplication is done in 32 bits and only the (already wrapped) result is widened. The cast is in the wrong place.

## Root cause

The product of two `u32` values was computed in 32 bits and widened afterwards, so any total above 4,294,967,295 wrapped silently in release builds.

## Fix

Widen first: `u64::from(chunks) * u64::from(chunk_size)`. Even the largest inputs (`u32::MAX` x `u32::MAX`) fit in a `u64`.

## Why the regression test would have caught it

It uses a value above the 32-bit limit (5,000 x 1 MiB) and the largest possible inputs, and it runs with the release profile, so it fails on the wrapped value (`left: 947912704, right: 5242880000`) instead of depending on a debug-only panic. Deliberate break: restoring the cast-after-multiply fails two of the three tests; the small-upload test still passes, which is why that bug survives casual testing.

## How to spot this class next time

- Different results in debug and release for the same input: think overflow first.
- In Rust, `as` never fails; it silently truncates or reinterprets. Prefer `From`, `try_from`, and `checked_*` for arithmetic on sizes.
- Test with values beyond the type's range, and run the tests in the profile you ship.

## Limits

The fix removes this overflow by widening. If inputs can be 64-bit too, use `checked_mul` and return an error. A project could also enable `overflow-checks` in release, at a cost in speed.
