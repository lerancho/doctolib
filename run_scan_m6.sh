#!/data/data/com.termux/files/usr/bin/sh
set -eu
# Always run from the project directory
cd "$(dirname "$0")"
# Ensure logs directory exists
mkdir -p logs
# Launch scan for RDV alias m6 and practitioner criton
python scan.py -rdv m6 -prat criton >> logs/scan-m6.log 2>&1
