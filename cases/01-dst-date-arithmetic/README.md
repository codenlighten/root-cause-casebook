# 01. The 9 o'clock reminder that arrives at 10 (Python)

> **Constructed example.** This bug was written for this repository to demonstrate a diagnosis method. It is not a report from any client, employer or production system.

## Symptom (as a user would report it)

"My daily 9:00 reminder fired at 10:00 on Sunday, 8 March. It was fine all week."

## Reproduce

```bash
./run-case.sh 1
```

## Investigation

1. **Narrow by date.** Listing the next 14 occurrences for one reminder showed every one at 09:00 except the one on 2026-03-08, and later (in autumn) one at 08:00 on 2026-11-01. Both are the days US clocks change. A bug that appears only on two days a year points at time-zone rules, not at the scheduler loop.
2. **Hypothesis: the time-zone database is wrong or outdated.** Rejected. `ZoneInfo("America/New_York")` reports UTC-5 on 7 March and UTC-4 on 8 March, which is correct, so the data is fine.
3. **Hypothesis: the server runs in the wrong zone.** Rejected. The function only ever sees aware datetimes, so the process zone is not consulted.
4. **Minimal repro.** One call: `next_daily(datetime(2026,3,7,9,0,tzinfo=NY))` returned `2026-03-08 10:00`. Printing the intermediate value showed `2026-03-08T14:00:00+00:00` after the "+1 day" step, which is 24 elapsed hours, not "the same wall time tomorrow".
5. **Root cause confirmed** by changing only that line and re-running the repro: the result became 09:00 on both transition days.

## Root cause

The code converted to UTC before adding `timedelta(days=1)`, so it added 24 elapsed hours instead of one calendar day, and a day that has 23 or 25 hours moved the wall-clock time.

## Fix

Add the day to the aware local datetime (Python keeps the wall time and looks the offset up again): `return at + timedelta(days=1)`. The diff is printed by `./run-case.sh 1`.

## Why the regression test would have caught it

It pins the two transition days (spring forward and fall back) as well as an ordinary day. Any test written only with "tomorrow" in June passes on the broken code, which is how this class ships. Deliberate break: restoring the UTC round trip makes both transition tests fail (10:00 and 08:00 instead of 09:00) while the ordinary-day test still passes.

## How to spot this class next time

- "Wrong by exactly one hour, on only some days" means DST until proven otherwise.
- Decide whether the rule is a wall-clock rule ("every day at 9") or an elapsed-time rule ("every 24 hours") before choosing the arithmetic.
- Test the two transition days of the zone that matters, and write down the expected wall time.

## Limits

A wall time that does not exist (02:30 on spring-forward day) or exists twice (01:30 on fall-back day) is not handled here; a real scheduler needs a stated policy for those.
