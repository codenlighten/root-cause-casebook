#!/usr/bin/env bash
cd "$1" && python3 -m unittest -v test_resolver 2>&1
