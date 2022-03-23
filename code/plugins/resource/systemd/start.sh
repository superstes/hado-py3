#!/bin/bash
set -e

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
source "${script_dir}/util.sh"

sudo systemctl start "$SVC"
exit 0
