#!/usr/bin/env bash
cd "$1" && go test -count=1 -run Deterministic ./... 2>&1
