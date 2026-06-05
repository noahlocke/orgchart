#!/usr/bin/env bash
# Rebuild the org chart. Examples:
#   ./build.sh            # data/orgchart.csv -> dist/orgchart.html
#   ./build.sh --sample   # build the bundled demo
cd "$(dirname "$0")" || exit 1
python3 build.py "$@"
