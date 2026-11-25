#!/usr/bin/env bash
cd "$1" && python3 -m unittest -v test_schedule 2>&1
