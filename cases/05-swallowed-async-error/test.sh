#!/usr/bin/env bash
cd "$1" && node --test --test-reporter=spec notify.test.ts 2>&1 | grep -v -e ExperimentalWarning -e 'node --trace-warnings'
exit "${PIPESTATUS[0]}"
