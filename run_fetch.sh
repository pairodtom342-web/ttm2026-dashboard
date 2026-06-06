#!/bin/bash
# รัน fetch_data.py อัปเดต data.json (เรียกโดย launchd ทุก N วินาที)
cd "/Users/pairod415/Desktop/Project_Life/carbonMICE Platform/carbonMICE Agent/Events/Event Expo/2026-05/eb5b4a15_20260520_Thailand-Travel-Mart-TTM_Chonburi/dashboard-app" || exit 1
PY=/Library/Frameworks/Python.framework/Versions/3.12/bin/python3
echo "=== $(date '+%F %T') start ===" >> fetch.log
"$PY" fetch_data.py >> fetch.log 2>&1
echo "=== $(date '+%F %T') end (exit $?) ===" >> fetch.log
