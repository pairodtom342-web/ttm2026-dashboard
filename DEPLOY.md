# Deploy → Public Link (GitHub Pages + GitHub Action)

ได้ลิงก์สาธารณะ `https://<USER>.github.io/<REPO>/` ที่ลูกค้าเปิดเองได้ + ข้อมูลรีเฟรช
อัตโนมัติทุก ~5 นาที (GitHub Action ดึง Sheet+Live → push ไป branch `data` → หน้าเว็บดึง raw)

> โค้ดนี้ **commit ไว้แล้ว** (git, branch `main`) และ **ไม่มี secret ในโค้ด** (รหัสอยู่ใน Secrets)
> สถาปัตยกรรม: `main` = โค้ด (Pages เสิร์ฟ, ไม่ rebuild บ่อย) · `data` = data.json (Action อัปเดต)

---

## 1) สร้าง repo (public) แล้ว push
- ไปที่ github.com → **New repository** → ตั้งชื่อเช่น `ttm2026-dashboard` → **Public** → Create (อย่าติ๊ก add README)
- push โค้ด (repo commit ไว้แล้ว เหลือแค่ต่อ remote):
```bash
cd "<...>/dashboard-app"
git remote add origin https://github.com/<USER>/<REPO>.git
git push -u origin main
```
> push จะถาม username + password → **password ใส่ Personal Access Token** (github.com → Settings → Developer settings → Personal access tokens → Fine-grained → ให้สิทธิ์ Contents: Read and write กับ repo นี้)
> *ทางเลือกง่ายกว่า:* ใช้แอป **GitHub Desktop** ลากโฟลเดอร์ dashboard-app เข้าไป publish ได้เลย

## 2) ใส่ Secrets (Settings → Secrets and variables → Actions → New repository secret)
| Name | Value |
|---|---|
| `CARBONMICE_EMAIL` | `carbonformevent@gmail.com` |
| `CARBONMICE_PASSWORD` | (รหัส carbonMICE — อยู่ใน `creds.local.json`) |
| `GOOGLE_TOKEN_JSON` | **เนื้อหาทั้งไฟล์** `<AgentRoot>/Carby/token.json` |

ก็อปค่าใส่ clipboard ได้สะดวก (รันใน Terminal — ไม่โชว์บนจอ):
```bash
# Google token → clipboard แล้วเอาไปวางในช่อง GOOGLE_TOKEN_JSON
cat "<AgentRoot>/Carby/token.json" | pbcopy
```

## 3) เปิด GitHub Pages
Settings → **Pages** → Source = **Deploy from a branch** → Branch: **main** · folder **/(root)** → Save
→ รอ 1–2 นาที ได้ลิงก์ `https://<USER>.github.io/<REPO>/`

## 4) รัน Action ครั้งแรก (สร้าง branch `data`)
แท็บ **Actions** → "Refresh TTM+ carbon data" → **Run workflow**
→ จะสร้าง branch `data` พร้อม `data.json` (หน้าเว็บถึงจะมีข้อมูล)
> หลังจากนี้ Action รันเองทุก 5 นาที (cron GitHub ขั้นต่ำ 5 นาที อาจดีเลย์เล็กน้อย)

## 5) เปิดลิงก์
`https://<USER>.github.io/<REPO>/` → dashboard live · อัปเดตเอง · กดปุ่ม ⛶ เต็มจอบนทีวี
หน้าเว็บ derive raw URL ของ branch `data` อัตโนมัติ (ไม่ต้องแก้อะไรในโค้ด)

---

## แก้ข้อมูล / ปรับความถี่
- แก้ตัวเลข → กรอกใน Google Sheet (แท็บ Participants / Waste) → ขึ้นเองรอบ Action ถัดไป
- คาร์บอน + Scope = ดึง Live carbonMICE อัตโนมัติ
- เปลี่ยนความถี่: แก้ `cron` ใน `.github/workflows/refresh-data.yml`

## Troubleshooting
- **หน้าเว็บขึ้น "Could not load"** → ยังไม่ได้รัน Action (ข้อ 4) หรือ branch `data` ยังไม่มี
- **Action แดง** → เช็ค Secrets ครบ 3 ตัว + token.json ยังไม่หมดอายุ (refresh_token ต้องใช้ได้)
- **ข้อมูลไม่อัปเดต** → ดู raw `https://raw.githubusercontent.com/<USER>/<REPO>/data/data.json` ว่าใหม่ไหม

## รัน/ทดสอบในเครื่อง (local)
```bash
bash serve_local.sh     # เสิร์ฟ + auto-refresh → http://localhost:8099
```
(local ใช้ `creds.local.json` + `Carby/token.json` · หน้าเว็บใช้ data.json ในเครื่อง)
