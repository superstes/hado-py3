#!/bin/bash
set -e

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
source "${script_dir}/util.sh"

sudo ip address del "$IP_CIDR" dev "$DEV"
exit 0