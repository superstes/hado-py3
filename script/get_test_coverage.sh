#!/usr/bin/env bash

# shellcheck disable=SC2164
cd "$(dirname "$0")"
cd "../code/lib"
python3 -m pytest ../test/ --cov=./ --cov-report=xml --cov-report=term:skip-covered
