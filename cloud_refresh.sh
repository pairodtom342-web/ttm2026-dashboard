#!/bin/bash
# ── อัปเดตข้อมูล "ขึ้น cloud" จากเครื่องนี้ (IP ไทย) ──
# carbonMICE (pea.co.th) บล็อก IP ของ GitHub (403) → ดึง live จาก CI ไม่ได้
# ดังนั้นเครื่องนี้ทำหน้าที่: ดึง Sheet+Live → push data.json ไป branch "data"
# → GitHub Pages (สาธารณะ) ดึง data.json จาก branch data ไปแสดง
#
# วิธีใช้ (ช่วงงาน เปิด Terminal ค้างไว้):
#     bash cloud_refresh.sh
# กด Ctrl+C เพื่อหยุด · ปรับความถี่ที่ตัวแปร REFRESH

cd "$(dirname "$0")" || exit 1
PY=/Library/Frameworks/Python.framework/Versions/3.12/bin/python3
REFRESH=120                                  # วินาที
ORIGIN=$(git remote get-url origin)
PUB=/tmp/ttm_pubdata

echo "────────────────────────────────────────────"
echo "  TTM+2026 — Cloud data updater"
echo "  push → branch data ของ $ORIGIN ทุก ${REFRESH} วิ"
echo "  เว็บสาธารณะ: https://pairodtom342-web.github.io/ttm2026-dashboard/"
echo "  Ctrl+C เพื่อหยุด"
echo "────────────────────────────────────────────"

while true; do
  if "$PY" fetch_data.py >> fetch.log 2>&1; then
    rm -rf "$PUB" && mkdir -p "$PUB" && cp data.json "$PUB/"
    if ( cd "$PUB" && git init -q && git config user.email carbonmice@pea.co.th && git config user.name carbonMICE \
         && git checkout -q -b data && git add data.json && git commit -qm "data: $(date -u +%FT%TZ)" \
         && git push -f -q "$ORIGIN" data:data ); then
      echo "[$(date '+%H:%M:%S')] ✅ ดึง+push ขึ้น cloud แล้ว"
    else
      echo "[$(date '+%H:%M:%S')] ⚠️ push ล้มเหลว (เช็ค gh auth / เน็ต)"
    fi
  else
    echo "[$(date '+%H:%M:%S')] ⚠️ fetch ล้มเหลว (ดู fetch.log)"
  fi
  sleep "$REFRESH"
done
