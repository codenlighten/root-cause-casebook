#!/usr/bin/env bash
# Query plans and one timing for the same request, on the same seeded data.
here=$(cd "$(dirname "$0")" && pwd)
cd "$1" && PYTHONPATH="$1" python3 "$here/bench.py"
