#!/usr/bin/env bash
# Runs every case (broken must fail, fixed must pass, reverted fix must fail) and prints a table.
set -u
root=$(cd "$(dirname "$0")" && pwd)
bad=0
printf '%-4s %-26s %-13s %-8s %-8s %-9s\n' "#" "case" "language" "broken" "fixed" "reverted"
for d in "$root"/cases/*/; do
  name=$(basename "$d"); n=${name%%-*}; title=${name#*-}
  lang=$(cat "$d/LANG")
  res=$("$root/run-case.sh" "$((10#$n))" --quiet 2>&1 | grep '^RESULT' || true)
  if [ "$res" = "RESULT broken=fail fixed=pass reverted=fail" ]; then
    printf '%-4s %-26s %-13s %-8s %-8s %-9s\n' "$n" "$title" "$lang" "fails" "passes" "fails"
  else
    printf '%-4s %-26s %-13s %s\n' "$n" "$title" "$lang" "UNEXPECTED (run ./run-case.sh $((10#$n)))"; bad=1
  fi
done
echo
if [ $bad -eq 0 ]; then echo "all cases behave as expected: broken fails, fix passes, partly reverted fix fails"; else echo "some cases did not behave as expected"; fi
exit $bad
