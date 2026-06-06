# TTM+ 2026 — Carbon Neutral Live Dashboard

Public real-time dashboard สำหรับงาน **Thailand Travel Mart Plus (TTM+) 2026**
(จัดโดย ททท. · นงนุชพัทยา ชลบุรี · 10–12 มิ.ย. 2569) ตามโจทย์ในไฟล์
`Input Output Display Dashboard TTM+2026.pdf`

## ไฟล์ในโฟลเดอร์
```
dashboard-app/
├── index.html        ← หน้า dashboard (self-contained: HTML+CSS+JS, ไม่มี dependency ภายนอก)
├── data.json         ← ข้อมูล carbon ล่าสุด (frontend อ่านไฟล์นี้ทุก 30 วิ)
├── fetch_data.py     ← สคริปต์ดึงข้อมูลจาก carbonMICE + Zero Waste Sheet → เขียน data.json
└── assets/           ← พื้นหลัง KV, โลโก้งาน/ผู้สนับสนุน, โลโก้ carbon neutral, ฟอนต์ TATSana Chon
```

## ทำอะไรได้ (ครบตาม brief)
- ดึง **ปริมาณคาร์บอนจริง** จากหน้า Dashboard carbonMICE (Scope 1/2/3 + รวม + แยกหมวด)
- ดึง **Zero Waste to landfills** จาก Google Sheet (เปิด public อ่าน CSV)
- เทียบ **จำนวนต้นไม้** ที่ดูดซับคาร์บอนได้ (1 ต้น ≈ 9.5 kgCO₂/ปี ตาม convention)
- ชื่องาน / ผู้จัด / สถานที่ / วันที่ / **นาฬิกา real-time (ICT)** / สถานะงาน (Upcoming / LIVE / Completed)
- ข้อมูลเป็น **ภาษาอังกฤษทั้งหมด**, ธีมจาก KV (sunset beach, ฟอนต์ TATSana Chon, glassmorphism)
- **Auto-refresh ทุก 30 วิ ไม่ต้องกด** + animation ตอนตัวเลขเปลี่ยน (flash + count-up)
- Animation: ใบไม้ปลิว, เมฆลอย, ต้นไม้โยก, light-sweep บน container
- ปุ่ม **Fullscreen**, รองรับ **TV 16:9 แนวนอน + แนวตั้ง** และ **มือถือ** (auto layout)

## รันทดสอบในเครื่อง
```bash
cd dashboard-app
python3 fetch_data.py          # อัปเดต data.json (ต้องมี playwright + chromium)
python3 -m http.server 8099    # เปิด http://localhost:8099  (ต้องเสิร์ฟผ่าน http ไม่ใช่ดับเบิลคลิกไฟล์)
```

## รันในเครื่องแบบ auto-refresh (แนะนำสำหรับ local)
เปิด **Terminal** แล้วรันสคริปต์เดียวจบ (เสิร์ฟหน้าเว็บ + ดึงข้อมูลใหม่อัตโนมัติ):
```bash
bash serve_local.sh        # เปิด http://localhost:8099 · refresh ทุก 120 วิ · Ctrl+C หยุด
```
- แก้ Google Sheet → dashboard เปลี่ยนเองภายใน ~120 วิ (รอบ fetch) + ≤30 วิ (poll หน้าเว็บ) ≈ **ไม่เกิน ~2.5 นาที**
- ปรับความถี่ได้ที่ตัวแปร `REFRESH` ในไฟล์ (เช่น 60 วิระหว่างวันงาน)
- ต้องเปิด Terminal ค้างไว้ (ปิด Terminal = หยุด)

> **ทำไมไม่ใช้ cron/launchd?** macOS บล็อก cron/launchd ไม่ให้เข้าโฟลเดอร์ Desktop (TCC →
> "Operation not permitted"). ถ้าต้องการให้รันเองตลอด (ไม่ต้องเปิด Terminal) มี 2 ทาง:
> (ก) ให้สิทธิ์ **Full Disk Access** กับ `/bin/bash` ใน System Settings แล้วโหลด
> `~/Library/LaunchAgents/com.carbonmice.ttm-dashboard.plist` (`launchctl load -w …`), หรือ
> (ข) **deploy ขึ้น cloud** (ด้านล่าง) — เหมาะกับ production ที่สุด

## เผยแพร่เป็น Public Link (ให้ลูกค้าเปิดเอง ไม่ต้อง run local)
**แนะนำ: Vercel (static) + GitHub Actions (รีเฟรช data.json)** — ฟรี + เป็น public URL จริง

1. push โฟลเดอร์นี้ขึ้น GitHub repo
2. import เข้า Vercel → ได้ลิงก์ `https://ttm2026-carbon.vercel.app` (static ไม่ต้อง build)
3. ตั้ง GitHub Action ตารางเวลา (เช่นทุก 2–5 นาที) ให้รัน `fetch_data.py` แล้ว commit `data.json`
   → Vercel redeploy อัตโนมัติ → หน้าเว็บดึง `data.json` ใหม่เองทุก 30 วิ

> ต้องการ **push แบบ instant จริงๆ (ไม่หน่วงเลย)** → ใช้ Supabase: ให้ `fetch_data.py`
> เขียนลงตาราง Supabase แล้ว frontend subscribe `realtime` แทนการ poll `data.json`
> (โครงข้อมูลใน `data.json` พร้อมย้ายลง Supabase ได้ทันที)

## หมายเหตุข้อมูลปัจจุบัน
ตอนนี้ total = **92.69 kgCO₂eq** เพราะ survey ยังเก็บไม่ครบ (งานยังไม่จัด) — ตัวเลข
จะเพิ่มขึ้นเองเมื่อมีผู้ตอบแบบสำรวจมากขึ้น และ Zero Waste จะเริ่มมีค่าในวันงาน
dashboard ออกแบบให้รองรับค่าว่าง/ศูนย์และอัปเดตเพิ่มได้แบบ real-time
