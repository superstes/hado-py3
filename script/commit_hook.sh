#!/usr/bin/env bash
set -e

# shellcheck disable=SC2164
cd "$(dirname "$0")"

bash ./run_lint.sh
bash ./run_tests.sh
