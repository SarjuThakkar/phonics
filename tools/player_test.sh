#!/usr/bin/env bash
# Drive every activity type in the player and report which ones a child could
# actually get past. Catches the class of bug that renders fine and then traps
# you on the screen -- which a screenshot will never show.
#
# Usage:  tools/player_test.sh [day]     (default: whatever days exist, plus
#                                         synthetic sentence/sightWord/story)
set -euo pipefail
cd "$(dirname "$0")/.."

PORT=8099
cp tools/player-test/drive.html web/_drive.html
trap 'rm -f web/_drive.html' EXIT

(cd web && timeout 180 python3 -m http.server "$PORT" >/dev/null 2>&1 &)
sleep 2

timeout 150 chromium --headless --disable-gpu --no-sandbox \
  --virtual-time-budget=120000 --dump-dom "http://localhost:$PORT/_drive.html" 2>/dev/null \
  | sed -n '/<!--RESULT/,/END/p' | sed 's/<!--RESULT//; s/END-->.*//'
