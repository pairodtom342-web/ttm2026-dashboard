# Deploy → Public Link (Vercel + GitHub Action)

เป้าหมาย: ได้ลิงก์สาธารณะ เช่น `https://ttm2026-carbon.vercel.app` ที่ลูกค้าเปิดเองได้
และข้อมูล carbon รีเฟรชอัตโนมัติทุก ~5 นาที (หน้าเว็บดึง `data.json` ใหม่เองทุก 30 วิ)

> ใช้ **โฟลเดอร์ `dashboard-app/` นี้เป็น root ของ repo** (push เฉพาะข้างในโฟลเดอร์นี้)

---

## 1) สร้าง GitHub repo แล้ว push
```bash
cd dashboard-app
git init
git add .
git commit -m "TTM+ 2026 live carbon dashboard"
git branch -M main
git remote add origin https://github.com/<user>/ttm2026-carbon.git
git push -u origin main
```

## 2) ใส่ GitHub Secrets (สำหรับ Action login carbonMICE)
ไปที่ repo → **Settings → Secrets and variables → Actions → New repository secret** เพิ่ม 2 ตัว:

| Name | Value |
|---|---|
| `CARBONMICE_EMAIL` | `carbonformevent@gmail.com` |
| `CARBONMICE_PASSWORD` | `Cfevent2025*` |

> Action `.github/workflows/refresh-data.yml` จะรัน `fetch_data.py` ทุก 5 นาที
> แล้ว commit `data.json` กลับ repo (กดรันเองได้ที่แท็บ **Actions → Refresh TTM+ carbon data → Run workflow**)
> หมายเหตุ: cron ของ GitHub ขั้นต่ำ 5 นาที และบางครั้งอาจดีเลย์ — ปกติสำหรับงาน live

## 3) เชื่อม Vercel (static, ไม่ต้อง build)
1. เข้า vercel.com → **Add New → Project** → import repo `ttm2026-carbon`
2. ตั้งค่า:
   - **Framework Preset:** `Other`
   - **Build Command:** เว้นว่าง / ปิด
   - **Output Directory:** `.` (root)
3. **Deploy** → ได้ public URL ทันที

ทุกครั้งที่ Action commit `data.json` ใหม่ → Vercel redeploy เอง → หน้าเว็บอัปเดต

---

## เปิดบนทีวี / จอแสดงผล
- เปิด URL บนเบราว์เซอร์ → กดปุ่ม **⛶ (มุมขวาบน)** เพื่อ Fullscreen
- TV แนวนอน 16:9 และแนวตั้ง รวมถึงมือถือ จัด layout ให้อัตโนมัติ
- ไม่ต้องกด refresh — ข้อมูลอัปเดตเองทุก 30 วิ และมี animation ตอนตัวเลขเปลี่ยน

## อยากได้ instant push (ไม่มีดีเลย์ 5 นาทีเลย) → ต่อยอด Supabase
ให้ `fetch_data.py` เขียนลงตาราง Supabase แทนการเขียนไฟล์ แล้วแก้ `index.html`
ให้ subscribe `supabase.channel(...).on('postgres_changes', ...)` แทนการ poll `data.json`
(โครง JSON ปัจจุบันย้ายลงตารางได้ตรงๆ) — บอกได้ถ้าต้องการให้ทำส่วนนี้
