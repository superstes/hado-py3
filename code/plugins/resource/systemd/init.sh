#!/bin/bash
set -e

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
source "${script_dir}/util.sh"

# making sure the service won't auto-start as that would lead to a possible active-active state
sudo systemctl disable "$SVC"
exit 0
