import requests
import time
import os
from datetime import datetime

# ================== AMBIL DARI ENV / GITHUB SECRETS ==================
BASE_URL           = os.getenv("BASE_URL").rstrip("/")
REFRESH_TOKEN      = os.getenv("REFRESH_TOKEN")
FAMILY_CODE        = os.getenv("FAMILY_CODE")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_USER_ID   = os.getenv("TELEGRAM_USER_ID")        
# ================== UBAH FILTER ORDER DI SINI SAJA ==================
# Ganti sesuai yang kamu mau, contoh:
#WANTED_ORDERS = [200, 199, 198]  # UBAH DI SINI SESUAI KEBUTUHAN!

#Kuota Utama 1.25GB  order 200
#Kuota Youtube & Tiktok 3.13GB  order 199
#Kuota Malam 3.75GB order 198

# WANTED_ORDERS = [1]             ← cuma order 1
WANTED_ORDERS = None           # ← redeem SEMUA paket (tanpa filter)

# ================== KIRIM TELEGRAM (HANYA 1 USER) ==================
def kirim_telegram(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_USER_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={
                "chat_id": TELEGRAM_USER_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            },
            timeout=10
        )
    except:
        pass

# ================== AMBIL LIST PAKET ==================
def ambil_paket():
    try:
        r = requests.post(
            f"{BASE_URL}/list",
            json={"refreshToken": REFRESH_TOKEN, "familyCode": FAMILY_CODE},
            timeout=30
        )
        r.raise_for_status()
        data = r.json()

        paket = []
        for variant in data.get("package_variants", []):
            for opt in variant.get("package_options", []):
                code  = opt.get("package_option_code")
                order = opt.get("order")
                name  = opt.get("name", "Unknown")
                if code and (WANTED_ORDERS is None or order in WANTED_ORDERS):
                    paket.append({"code": code, "order": order, "name": name})
        return paket
    except Exception as e:
        kirim_telegram(f"<b>GAGAL AMBIL LIST</b>\n{str(e)[:100]}")
        return []

# ================== REDEEM ==================
def redeem(info):
    for _ in range(3):
        try:
            r = requests.post(
                f"{BASE_URL}/dor",
                json={"refreshToken": REFRESH_TOKEN, "packageCode": info["code"]},
                timeout=30
            )
            if r.status_code == 200:
                trx = r.json().get("transaction_code", "N/A")
                return True, f"BERHASIL | {info['name']} | Trx: {trx}"
            else:
                return False, f"GAGAL {r.status_code} | {r.text[:100]}"
        except:
            time.sleep(2)
    return False, "KONEKSI GAGAL"

# ================== JALANKAN BOT ==================
print(f"Redeem Bot Start → {datetime.now():%d/%m/%Y %H:%M:%S}")
kirim_telegram(f"<b>REDEEM BOT MULAI</b>\n{datetime.now():%d/%m/%Y %H:%M:%S}")

daftar = ambil_paket()
if not daftar:
    kirim_telegram("<b>TIDAK ADA PAKET / GAGAL LIST</b>")
    exit()

kirim_telegram(f"<b>Ditemukan {len(daftar)} paket</b>\nFilter: {WANTED_ORDERS or 'SEMUA'}")

sukses = gagal = 0
for i, p in enumerate(daftar, 1):
    print(f"[{i}/{len(daftar)}] Order {p['order']} → {p['name']}")
    ok, pesan = redeem(p)
    if ok:
        sukses += 1
        msg = f"<b>SUKSES #{sukses}</b>\n{pesan}\n<code>{p['code']}</code>"
    else:
        gagal += 1
        msg = f"<b>GAGAL #{gagal}</b>\nOrder {p['order']} | {p['name']}\n{pesan}"
    kirim_telegram(msg)
    time.sleep(3.5)

summary = f"""
<b>REDEEM SELESAI!</b>
Berhasil : {sukses}
Gagal    : {gagal}
Total    : {len(daftar)}
Filter   : {WANTED_ORDERS or "SEMUA"}
Selesai  : {datetime.now():%H:%M:%S}
"""
print(summary.strip())
kirim_telegram(summary)
