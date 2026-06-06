#!/usr/bin/env python3
"""
fetch_data.py — รวมข้อมูล TTM+2026 dashboard → data.json

แหล่งข้อมูล (ตามที่ลูกค้ากำหนด):
  ซ้าย • Participants (Sellers/Buyers/Staff)  ← Google Sheet แท็บ "Participants" (กรอกเอง)
  ซ้าย • คาร์บอนรวม + Scope 1/2/3            ← Live carbonMICE dashboard API
  ซ้าย • ต้นไม้ offset                        ← สูตร = คาร์บอนรวม(kg) ÷ 9.5
  ขวา  • ขยะ 3 ประเภท + รายวัน + GHG ลดได้   ← Google Sheet แท็บ "Waste" (กรอกเอง)
  ขวา  • ต้นไม้                               ← สูตร = GHG(kg) ÷ 9.5

รันซ้ำ/cron ได้. ต้องมี: gspread, google-auth, playwright(chromium)
"""
import asyncio, json, os, datetime
from pathlib import Path
import gspread
from google.oauth2.credentials import Credentials
from playwright.async_api import async_playwright

HERE      = Path(__file__).resolve().parent
OUT_FILE  = HERE / "data.json"
AGENT_DIR = HERE.parents[4]                       # .../carbonMICE Agent
TOKEN     = AGENT_DIR / "Carby" / "token.json"    # Google token (scope: spreadsheets)

AUTH_URL  = "https://carbonform.pea.co.th"
PLATFORM  = "https://carbonmice.pea.co.th"

# ── credentials (ไม่ฝังในโค้ด/ไม่ขึ้น repo) ──────────────────────────────────
#   cloud  : ตั้งเป็น env (GitHub Secrets) CARBONMICE_EMAIL / CARBONMICE_PASSWORD
#   local  : ใส่ในไฟล์ creds.local.json {"email":..,"password":..} (อยู่ใน .gitignore)
def _load_creds():
    email = os.environ.get("CARBONMICE_EMAIL", "").strip()
    pw    = os.environ.get("CARBONMICE_PASSWORD", "").strip()
    f = HERE / "creds.local.json"
    if (not email or not pw) and f.exists():
        d = json.loads(f.read_text(encoding="utf-8"))
        email = email or d.get("email", "")
        pw    = pw or d.get("password", "")
    return email, pw

EMAIL, PASSWORD = _load_creds()

EVENT_ID  = os.environ.get("TTM_EVENT_ID", "eb5b4a15-268c-4c60-bc5b-250f488560c0")
SHEET_ID  = os.environ.get("TTM_SHEET_ID", "1uCSoxxNNlPxCAmG30Zuf-i-KiuT5LLdOIa4oAWLx7JE")

KG_PER_TREE = 9.5                                 # ต้นไม้ 1 ต้น ดูดซับ 9.5 kgCO₂eq/ปี

WASTE_COLORS = ["#5FB97A", "#3E86C9", "#E8956B"]  # Composting / RDF / Recyclables

EVENT = {
    "nameEN": "Thailand Travel Mart Plus (TTM+) 2026",
    "organizer": "Tourism Authority of Thailand",
    "venue": "Nong Nooch Pattaya International Convention & Exhibition Center",
    "province": "Chonburi, Thailand",
    "dateLabel": "10 – 12 June 2026",
    "startDate": "2026-06-10", "endDate": "2026-06-12",
    "carbonNeutral": True, "standard": "ISO 14064-1:2018",
}
SCOPE_DESC = {
    "Scope 1": "Direct emissions from the event",
    "Scope 2": "Indirect emissions from energy",
    "Scope 3": "Other indirect emissions",
}
BENEFITS = [
    {"icon": "🌍", "label": "Reduce environmental impact"},
    {"icon": "🚛", "label": "Reduce waste sent to disposal"},
    {"icon": "♻️", "label": "Increase resource value"},
    {"icon": "💡", "label": "Build sustainability awareness"},
]


def num(x):
    try: return float(str(x).replace(",", "").strip())
    except Exception: return 0.0


def disp_unit(total_kg):
    """เลือกหน่วยอัตโนมัติ: ≥1000kg → tCO₂e (÷1000), ไม่งั้น kgCO₂eq"""
    if total_kg >= 1000:
        return "tCO₂e", 1000.0
    return "kgCO₂eq", 1.0


# ── Google Sheet ────────────────────────────────────────────────────────────
def _gspread_client():
    """cloud: env GOOGLE_TOKEN_JSON (เนื้อ token.json) · local: ไฟล์ Carby/token.json"""
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    tok = os.environ.get("GOOGLE_TOKEN_JSON", "").strip()
    if tok:
        creds = Credentials.from_authorized_user_info(json.loads(tok), scopes)
    else:
        creds = Credentials.from_authorized_user_file(str(TOKEN), scopes)
    return gspread.Client(auth=creds)


def read_sheet():
    gc = _gspread_client()
    sh = gc.open_by_key(SHEET_ID)

    # Participants
    pv = sh.worksheet("Participants").get("A3:B5")
    items = []
    p_total = sum(num(r[1]) for r in pv if len(r) > 1)
    for r in pv:
        if len(r) >= 2 and r[0].strip():
            v = num(r[1])
            items.append({"label": r[0].strip(), "value": int(v),
                          "percent": round(v / p_total * 100, 1) if p_total else 0})
    respondents = {"total": int(p_total), "items": items}

    # Waste
    wv = sh.worksheet("Waste").get("A2:E9")
    days_raw = wv[0][1:4] if wv else []
    days = [d.split("\n")[-1].replace(" 2026", "").strip() for d in days_raw]
    cats, daily = [], []
    grand = 0.0
    for r in wv[1:4]:                              # rows: Composting, RDF, Recyclables
        if not r or not r[0].strip():
            continue
        i = len(cats)
        vals = [num(r[1]) if len(r) > 1 else 0, num(r[2]) if len(r) > 2 else 0, num(r[3]) if len(r) > 3 else 0]
        tot = num(r[4]) if len(r) > 4 else sum(vals)
        grand += tot
        cats.append({"label": r[0].strip(), "value": round(tot, 1), "color": WASTE_COLORS[i % 3]})
        daily.append({"label": r[0].strip(), "color": WASTE_COLORS[i % 3], "values": [round(v, 1) for v in vals]})
    for c in cats:
        c["percent"] = round(c["value"] / grand * 100, 1) if grand else 0
    # GHG reduced (row 8 = index 6 ของ A2:E9) คอลัมน์ B
    ghg_kg = num(wv[6][1]) if len(wv) > 6 and len(wv[6]) > 1 else 0.0

    waste = {"unitTotal": "kg", "total": round(grand, 1), "categories": cats, "days": days, "daily": daily}
    wr_unit, wr_div = disp_unit(ghg_kg)
    waste_reduction = {
        "unit": wr_unit, "value": round(ghg_kg / wr_div, 2),
        "trees": round(ghg_kg / KG_PER_TREE), "treeNote": "medium tree, 10 years old",
    }
    return respondents, waste, waste_reduction


# ── Live carbonMICE ─────────────────────────────────────────────────────────
async def read_live():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
        ctx = await b.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
            viewport={"width": 1366, "height": 900}, locale="th-TH")
        page = await ctx.new_page()
        page.set_default_timeout(60000)
        try:
            resp = await page.goto(f"{AUTH_URL}/auth/sign-in?redirect={PLATFORM}/", wait_until="domcontentloaded")
            print(f"   ↪ goto status={resp.status if resp else '?'} url={page.url}")
            # รอฟอร์ม login เรนเดอร์ (SPA — ใน CI ช้ากว่า local)
            try:
                await page.wait_for_selector('input[type="email"]', state="visible", timeout=45000)
            except Exception:
                title = await page.title()
                body = (await page.inner_text("body"))[:400] if await page.query_selector("body") else ""
                print(f"   🔎 no email field. title={title!r} bodyText={body!r}")
                raise
            await page.fill('input[type="email"]', EMAIL)
            await page.fill('input[type="password"]', PASSWORD)
            await page.click('button[type="submit"]')
            # รอ redirect กลับ platform (login สำเร็จ)
            try:
                await page.wait_for_url(lambda u: PLATFORM in u, timeout=45000)
            except Exception:
                await page.wait_for_timeout(4000)
            await page.wait_for_timeout(2000)
            r = await page.request.get(f"{PLATFORM}/api/dashboard/{EVENT_ID}/emission-detail")
            data = await r.json() if r.status == 200 else {}
            if r.status != 200:
                print(f"   ⚠️ emission-detail HTTP {r.status} (url={page.url})")
        except Exception as e:
            print(f"   ⚠️ login/fetch error: {type(e).__name__} url={page.url}")
            raise
        finally:
            await b.close()
    return (data or {}).get("TotalSummary", {})


def build_emissions(ts):
    total_kg = num(ts.get("summary", 0))
    unit, div = disp_unit(total_kg)
    sc = [("Scope 1", num(ts.get("scope1", 0))),
          ("Scope 2", num(ts.get("scope2", 0))),
          ("Scope 3", num(ts.get("scope3", 0)))]
    scopes = [{"name": n, "desc": SCOPE_DESC[n], "value": round(v / div, 2),
               "percent": round(v / total_kg * 100, 1) if total_kg else 0} for n, v in sc]
    emissions = {"unit": unit, "total": round(total_kg / div, 2), "scopes": scopes}
    offset = {"unit": unit, "value": round(total_kg / div, 2),
              "trees": round(total_kg / KG_PER_TREE), "treeNote": "medium tree, 10 years old"}
    return emissions, offset


def main():
    respondents, waste, waste_reduction = read_sheet()
    try:
        ts = asyncio.run(read_live())
        emissions, offset = build_emissions(ts)
        live_ok = True
    except Exception as e:
        print("⚠️ live fetch failed:", e)
        emissions = {"unit": "tCO₂e", "total": 0, "scopes":
                     [{"name": n, "desc": d, "value": 0, "percent": 0} for n, d in SCOPE_DESC.items()]}
        offset = {"unit": "tCO₂e", "value": 0, "trees": 0, "treeNote": "medium tree, 10 years old"}
        live_ok = False

    data = {
        "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": "Google Sheet (manual) + Live carbonMICE",
        "event": EVENT,
        "respondents": respondents,
        "emissions": emissions,
        "offset": offset,
        "waste": waste,
        "wasteReduction": waste_reduction,
        "benefits": BENEFITS,
    }
    OUT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ wrote data.json | live={'ok' if live_ok else 'FAIL'} "
          f"emissions={emissions['total']}{emissions['unit']} offset_trees={offset['trees']} "
          f"| waste={waste['total']}kg ghg_trees={waste_reduction['trees']} "
          f"| participants={respondents['total']}")


if __name__ == "__main__":
    main()
