#!/usr/bin/env bash
# The same test in a debug build: here the overflow panics instead of wrapping.
cd "$1" && cargo test --offline --quiet 2>&1 | grep -E 'panicked|overflow|assertion|left|right|test result' | head -n 8
