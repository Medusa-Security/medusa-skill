#!/usr/bin/env bash
set -euo pipefail

tmpdir="$(mktemp -d)"
trap 'rm -rf -- "$tmpdir"' EXIT

printf '%s\n' "$tmpdir"
