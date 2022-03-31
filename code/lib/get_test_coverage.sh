#!/bin/bash

# shellcheck disable=SC2164
cd "$(dirname "$0")"
python3 -m coverage run -m pytest ../test/
python3 -m coverage report -m
