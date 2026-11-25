#!/usr/bin/env bash
# Release profile on purpose: it is the build that ships, and it wraps instead of panicking.
# The build directory is local to the copy under test: a CARGO_TARGET_DIR shared between the
# broken, fixed and reverted copies lets cargo reuse one state's artifacts for another.
cd "$1" && CARGO_TARGET_DIR="$1/target" cargo test --release --offline --quiet 2>&1
