#!/bin/bash
set -e

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
source "${script_dir}/util.sh"

if ip address show dev "$DEV" 2>/dev/null | grep -q "$IP_CIDR"
then
  echo '1'
else
  echo '0'
fi
exit 0
