#!/usr/bin/env bash
set -euo pipefail
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp "${1:?Usage: bash decode_base64.sh INPUT_FILE}" "$work/current"
for ((i=0; i<50; i++)); do
    base64 --decode "$work/current" > "$work/next"
    mv "$work/next" "$work/current"
done
cat "$work/current"
printf '\n'
