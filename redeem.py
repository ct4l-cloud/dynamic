import requests
import time
import os
from datetime import datetime

# ================== GITHUB SECRETS (WAJIB) ==================
URL = os.getenv("REDEEM_URL")                    # contoh: https://kontolfyumak000.netlify.app/api/dor
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")       # token panjang kamu

# Optional (bisa di-override lewat secrets kalau mau ganti nomor)
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "6287785992494")

# ================== TELEGRAM CONFIG (PAKAI USER ID) ==================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8398072484:AAHEBgq0r7ipfYqdHySMOv-pT0ldeOwzWhE")

# MASUKKAN USER ID KAMU DI SINI (bisa lebih dari satu)
USER_IDS = [
    "6246739155",   # ← User ID utama kamu
    # "123456789",  # ← tambah kalau mau kirim ke orang lain juga
    # "987654321",
]

# ================== PACKAGE CODE (HARDCODE – BEBAS TAMBAH) ==================
package_codes = [
    "U0NfX1qZKOLx-DBeVeYPePQ2a1cscHGy8_a16I_DX0HJUxGR74TWkUsW6wz-Q3iGoibWuXNVqPIUTApZO0mkQciO",  # tiktok
    "U0NfX_3eaDg5yj-JW7LesPccRCIC5Z_uGilvgcfyMNN7AnSiIL-x3NKauuqsoo_Oj5LKH4h-yzYokcT2ChMI3tsw",  # utama
    "U0NfX4-0asSbUAcDNcHKkTlywZXG37WXVWmLaI0HABtMXQfdBMpurHxWrfFhHDFSpVwfyFKyWwjlfUgdlHkwL6aw",  # malam
    # Tambah package baru di sini ↓
    # "U0NfX_abc123...",
    # "U0NfX_xyz999...",
]

# ================== FUNGSI KIRIM TELEGRAM KE USER ID ==================
def kirim_telegram(text):
    for user_id in USER_IDS:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                data={
                    "chat_id": user_id.strip(),
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True
                },
                timeout=10
            )
            time.sleep(0.6)  # anti flood
        except:
            pass

# ================== FUNGSI REDEEM ==================
def redeem(code):
    payload = {
        "phoneNumber": PHONE_NUMBER,
        "refreshToken": REFRESH_TOKEN,
        "packageCode": code
    }
    try:
        r = requests.post(URL, json=payload, timeout=30)
        if r.status_code == 200:
            trx = r.json().get("transaction_code", "N/A")
            return True, f"BERHASIL | Trx: {trx}"
        else:
            return False, f"GAGAL {r.status_code}\n{r.text[:140]}".replace("<", "").replace(">", "")
    except Exception as e:
        return False, f"ERROR KONEKSI: {str(e)[:100]}"

# ================== MULAI EKSEKUSI ==================
print(f"Bot mulai: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
kirim_telegram(f"<b>Redeem Bot START!</b>\n{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\nTotal paket: {len(package_codes)}")

sukses = 0
gagal = 0

for i, code in enumerate(package_codes, 1):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Coba paket {i}/{len(package_codes)} → {code[:40]}...")
    
    status, pesan = redeem(code)
    
    if status:
        sukses += 1
        msg = f"<b>SUKSES #{sukses}</b>\n{pesan}\n<code>{code[:50]}...</code>"
    else:
        gagal += 1
        msg = f"<b>GAGAL #{gagal}</b>\n{pesan}"
    
    print(f"   → {pesan}")
    kirim_telegram(msg)
    time.sleep(3)  # jeda aman

# ================== SUMMARY AKHIR ==================
summary = f"""
<b>REDEEM SELESAI!</b>
Berhasil : {sukses}
Gagal    : {gagal}
Total    : {len(package_codes)}
Waktu    : {datetime.now().strftime('%H:%M:%S')}
"""
print(summary)
kirim_telegram(summary)
