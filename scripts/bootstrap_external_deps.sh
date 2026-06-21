#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

git -C "${root}" submodule update --init --recursive
"${root}/scripts/verify_external_deps.sh"
