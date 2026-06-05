#!/usr/bin/env bash
# Rebuild the org chart from orgchart.csv. Double-click or run: ./build.sh
cd "$(dirname "$0")" || exit 1
python3 build.py "$@"
echo
echo "Done. Open orgchart.html in your browser."
