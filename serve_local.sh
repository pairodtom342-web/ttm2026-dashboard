#!/bin/bash
# ── TTM+2026 Dashboard — รันในเครื่อง (เสิร์ฟหน้าเว็บ + auto-refresh ข้อมูล) ──
# วิธีใช้:  เปิด Terminal แล้วพิมพ์
#     bash "serve_local.sh"
# เปิดเบราว์เซอร์: http://localhost:8099   (กด Ctrl+C เพื่อหยุด)
#
# ทุก ๆ REFRESH วินาที จะรัน fetch_data.py (ดึง Google Sheet + Live carbonMICE)
# → เขียน data.json → หน้าเว็บอัปเดตเองภายใน ~30 วิ (ไม่ต้องกด refresh)

cd "$(dirname "$0")" || exit 1
PY=/Library/Frameworks/Python.framework/Versions/3.12/bin/python3
PORT=8099
REFRESH=120            # วินาที — ปรับได้ (เช่น 60 ระหว่างวันงาน)

# เสิร์ฟไฟล์ static
"$PY" -m http.server "$PORT" >/dev/null 2>&1 &
SRV=$!
trap 'echo; echo "หยุดแล้ว"; kill $SRV 2>/dev/null; exit 0' INT TERM

echo "────────────────────────────────────────────"
echo "  TTM+2026 Dashboard"
echo "  เปิด:  http://localhost:8099"
echo "  refresh ข้อมูลทุก ${REFRESH} วิ  ·  กด Ctrl+C เพื่อหยุด"
echo "────────────────────────────────────────────"

while true; do
  "$PY" fetch_data.py >> fetch.log 2>&1 \
    && echo "[$(date '+%H:%M:%S')] ✅ อัปเดต data.json แล้ว" \
    || echo "[$(date '+%H:%M:%S')] ⚠️ fetch ล้มเหลว (ดู fetch.log)"
  sleep "$REFRESH"
done
