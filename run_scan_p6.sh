#!/data/data/com.termux/files/usr/bin/sh
set -eu
# Always run from the project directory
cd "$(dirname "$0")"
# Ensure logs directory exists
mkdir -p logs
# Launch scan for RDV alias p6 and practitioner criton
python scan.py -rdv p6 -prat criton >> logs/scan-p6.log 2>&1
