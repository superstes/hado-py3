#!/usr/bin/env bash

# shellcheck disable=SC2164
cd "$(dirname "$0")"

GIT_DIR="$(git rev-parse --git-dir)"
ln -s commit_hook.sh "$GIT_DIR/hooks/pre-commit"
