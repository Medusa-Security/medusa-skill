#!/usr/bin/env bash
set -euo pipefail

tmpdir="$(mktemp -d)"
# Remove only the directory created above when the script exits, including on normal completion.
trap 'rm -rf -- "$tmpdir"' EXIT

printf '%s\n' "$tmpdir"
