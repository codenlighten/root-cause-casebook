# 05. "All 3 notifications sent" when one failed (TypeScript)

> **Constructed example.** This bug was written for this repository to demonstrate a diagnosis method. It is not a report from any client, employer or production system.

## Symptom

"The job says it sent 3 notifications. Bob never got his, nothing is in the error log, and every so often the worker process dies with an unhandled promise rejection."

## Reproduce

```bash
./run-case.sh 5
```

## Investigation

1. **Call the sender alone.** `send("bob")` rejects with "mailbox full" every time. The sender is correct and reports its failure; the loss is in the caller.
2. **Hypothesis: the `catch` is hiding the error.** Rejected. The `catch` never ran. Adding a log line inside it printed nothing, even when Bob's send was forced to fail.
3. **Read the control flow.** `users.forEach(async ...)` returns `undefined` and ignores the promises its callback returns. The `try` therefore wraps only the creation of the promises, which cannot throw. The function returns before any send finishes.
4. **Explain the crash.** Each ignored promise that rejects has no handler. Node reports it as an unhandled rejection after the function has returned. The test run shows it: "generated asynchronous activity after the test ended ... triggered an unhandledRejection event".
5. **Explain "sent = 3".** The count was `users.length` minus failures, and failures were never collected.

## Root cause

The sends were started inside `forEach(async ...)` and never awaited, so the function returned before the sends settled and their rejections went to no handler.

## Fix

`Promise.allSettled(users.map(send))`, then report each rejection with the user it belongs to. One failure no longer stops the other sends, and none is silently dropped.

## Why the regression test would have caught it

It awaits `notifyAll` with one sender that fails after a delay and asserts the failure list, the count and which users were delivered. The delay matters: a sender that fails synchronously can hide the bug. Deliberate break: replacing the await with a fire-and-forget loop that reports every send as fulfilled makes the test fail (empty failure list), matching the original symptom.

## How to spot this class next time

- `forEach` with an `async` callback is almost always a bug. Use `map` and await the result, or a `for ... of` loop.
- A `try/catch` only catches what is awaited inside it.
- Run Node with unhandled rejections as errors (the default since Node 15) and treat any such log line as a failing check.

## Limits

All sends start at once. A real job would bound concurrency and retry; that is deliberately left out to keep the lesson in one place.
