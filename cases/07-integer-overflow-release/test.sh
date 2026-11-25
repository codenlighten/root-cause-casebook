#!/usr/bin/env bash
# Release profile on purpose: it is the build that ships, and it wraps instead of panicking.
cd "$1" && cargo test --release --offline --quiet 2>&1
