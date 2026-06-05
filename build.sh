#!/usr/bin/env bash
# Build an org chart:  ./build.sh SOURCE NAME   ->  dist/NAME.html
# Examples:
#   ./build.sh data/orgchart.csv company       # -> dist/company.html
#   ./build.sh data/sales.csv    sales-team    # -> dist/sales-team.html
#   ./build.sh --sample                         # build the bundled demo
cd "$(dirname "$0")" || exit 1
python3 build.py "$@"
