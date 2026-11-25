#!/usr/bin/env bash
# Usage: ./run-case.sh <n> [--quiet]
# Runs one case in three states, each in a throwaway copy:
#   broken    the regression test must FAIL
#   fixed     the same test must PASS
#   reverted  the fix with part of it undone (break.patch) must FAIL again
set -u
root=$(cd "$(dirname "$0")" && pwd)
n=${1:?usage: ./run-case.sh <n> [--quiet]}
quiet=${2:-}
printf -v nn '%02d' "$((10#$n))" 2>/dev/null || { echo "case number must be 1-9" >&2; exit 2; }
case_dir=$(ls -d "$root"/cases/"$nn"-* 2>/dev/null | head -n1)
[ -n "$case_dir" ] || { echo "no case $nn" >&2; exit 2; }
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

say() { [ -n "$quiet" ] || printf '%s\n' "$*"; }

run_state() { # label, directory with the sources, expected: fail|pass
  local label=$1 src=$2 expect=$3 out status got
  out=$(bash "$case_dir/test.sh" "$src" 2>&1); status=$?
  [ $status -eq 0 ] && got=pass || got=fail
  say ""
  say "--- $label: expecting the test to $expect ---"
  say "$(printf '%s\n' "$out" | tail -n 22)"
  say "=> test $got"
  [ "$got" = "$expect" ]
}

say "=== case $nn: $(basename "$case_dir" | cut -d- -f2-) ==="
ok=1
cp -r "$case_dir/broken" "$work/broken"
cp -r "$case_dir/fixed" "$work/fixed"
cp -r "$case_dir/fixed" "$work/reverted"

run_state "broken (the bug)" "$work/broken" fail || ok=0
run_state "fixed" "$work/fixed" pass || ok=0

say ""
say "--- fix diff (broken -> fixed, tests are identical) ---"
say "$(cd "$case_dir" && diff -ru broken fixed | grep -v '^Only in' | head -n 60)"

( cd "$work/reverted" && patch -p1 -s < "$case_dir/break.patch" ) || { echo "break.patch does not apply" >&2; ok=0; }
run_state "fixed, then the fix deliberately reverted in part" "$work/reverted" fail || ok=0

if [ -z "$quiet" ] && [ -f "$case_dir/extra.sh" ]; then
  say ""
  say "--- extra evidence ---"
  for state in broken fixed; do
    say "[$state]"
    bash "$case_dir/extra.sh" "$work/$state" 2>&1 | tail -n 40
  done
fi

if [ $ok -eq 1 ]; then
  say ""; say "case $nn OK"
  [ -z "$quiet" ] || echo "RESULT broken=fail fixed=pass reverted=fail"
  exit 0
fi
[ -z "$quiet" ] || echo "RESULT unexpected"
exit 1
