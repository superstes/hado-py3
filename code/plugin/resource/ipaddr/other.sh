#!/usr/bin/env bash
set -e

TIMEOUT="0.2"

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
source "${script_dir}/util.sh"

timeout "$TIMEOUT" ping -c1 "$IP" -I "$DEV" -q >/dev/null 2>/dev/null

# shellcheck disable=SC2181
if [ "$?" == "0" ]
then
  echo 1
  exit 0
else
  timeout "$TIMEOUT" ping -c1 "$IP" -q >/dev/null 2>/dev/null
  if [ "$?" == "0" ]
  then
    echo 1
    exit 0
  else
    echo 0
    exit 1
  fi
fi
