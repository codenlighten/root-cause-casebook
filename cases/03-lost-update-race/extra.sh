#!/usr/bin/env bash
# The same bug as the race detector sees it, with 200 goroutines and no forced interleaving.
cd "$1" && go test -race -count=1 -run Stress ./... 2>&1 | head -n 24
