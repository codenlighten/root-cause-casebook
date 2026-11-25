#!/usr/bin/env bash
# Measured memory growth: 100,000 distinct lookups, each result about 1 KB.
here=$(cd "$(dirname "$0")" && pwd)
cd "$1" && PYTHONPATH="$1" python3 "$here/bench.py"
