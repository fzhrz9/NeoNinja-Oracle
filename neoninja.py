import os
import time
import schedule
import logging
import threading
import requests
from flask import Flask
import telebot

# =====================================================================
# KONFIGURASI ALPHAV3 (GRED INSTITUSI)
# =====================================================================
TELEGRAM_BOT_TOKEN = "8673710597:AAGD4I53588YSL1QK9ZllzlaeQY68gFttSQ"
VIP_CHANNEL_ID = "-1003943365561" 
ADMIN_ID = "970309251"            

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Parameter "Sweet Spot" Institusi
MIN_LIQUIDITY = 100000        
MIN_DROP_24H = -1.5           
ATH_DROP_RANGE = (-80, -40)   
RSI_RESET_ZONE = 45           
FIBO_POCKET = [0.5, 0.618]    

# Enjin 1: Senarai Naratif Mikro (The Core)
CORE_NARRATIVES = [
    'artificial-intelligence', 'ai-agents', 'infrastructure', 'depin', 
    'internet-of-things-iot', 'real-world-assets-rwa', 'liquid-restaking-tokens', 
    'modular-blockchain', 'telegram-bots', 'solana-ecosystem', 'base-ecosystem', 
    'memecoins', 'gaming'
]

signal_found_this_cycle = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - ALPHAV3 - %(levelname)s - %(message)s')

# =====================================================================
# MODUL BYPASS RENDER (DUMMY WEB SERVER)
# =====================================================================
app = Flask(__name__)

@app.route('/')
def health_check():
    return "AlphaV3 System Heartbeat: ONLINE (Render Bypass Active)"

def run_web_server():
    # Gunakan port dari environment Render, jika tiada guna 10000
    port = int(os.environ.get("PORT", 10000)) 
    app.run(host='0.0.0.0', port=port, use_reloader=False)

# =====================================================================
# MODUL 1: AMARAN PELAYAN (AUTO-BOOT)
# =====================================================================
def send_admin_reboot_alert():
    msg = (
        "🚨 *ALPHAV3 REBOOT DETECTED*\n\n"
        "Tuan, sistem baru sahaja dihidupkan semula akibat kitaran pelayan awan (cloud server). "
        "Radar Dual-Engine telah diaktifkan secara automatik (Auto-Scan). "
        "Tiada tindakan manual diperlukan. Sedia beroperasi."
    )
    try:
        bot.send_message(ADMIN_ID, msg, parse_mode="Markdown")
        logging.info("Auto-boot alert dihantar kepada Admin.")
    except Exception as e:
        logging.error(f"Gagal hantar amaran admin: {e}")

# =====================================================================
# MODUL 2: PAIP DATA & DUAL-ENGINE SCANNER
# =====================================================================
def get_coingecko_categories():
    url = "https://api.coingecko.com/api/v3/coins/categories"
    try:
        res = requests.get(url, timeout=10)
        return res.json() if res.status_code == 200 else []
    except Exception:
        return []

def engine_two_satellite_scan():
    logging.info("🔥 Mengaktifkan Enjin 2 (The Satellite)...")
    categories = get_coingecko_categories()
    if not categories: return

    valid_sectors = []
    for cat in categories:
        try:
            mcap_change = cat.get('market_cap_change_24h') or 0
            vol_24h = cat.get('volume_24h') or 0
            
            # Sweet Spot Enjin 2: Profit > 5% & Volume > $500M
            if mcap_change > 5.0 and vol_24h > 500000000:
                valid_sectors.append({
                    "name": cat['name'], "id": cat['id'], "profit": mcap_change
                })
        except Exception: continue

    valid_sectors = sorted(valid_sectors, key=lambda x: x['profit'], reverse=True)
    top_3 = valid_sectors[:3]
    
    if top_3:
        logging.info(f"Top 3 Sektor dikesan: {[s['name'] for s in top_3]}")
        # Di sini bot akan loop koin dalam top_3 dan hantar ke analyze_asset()
    else:
        logging.info("Tiada sektor melepasi Jaring Keuntungan Enjin 2 hari ini.")

def engine_one_core_scan():
    logging.info("⚙️ Mengaktifkan Enjin 1 (The Core)...")
    # Di sini bot akan tarik senarai koin dari CORE_NARRATIVES dan hantar ke analyze_asset()

# =====================================================================
# MODUL 3: TAPISAN SWEET SPOT & SMART MONEY (THE QUANT BRAIN)
# =====================================================================
def analyze_asset(coin_data):
    """
    Logik tapisan Gred Institusi.
    (Data di bawah adalah contoh struktur pengiraan. Sambungan API sebenar akan dimasukkan kemudian)
    """
    # 1. Fundamental & Liquidity Filter
    if coin_data["drop_24h"] > MIN_DROP_24H: return None
    if coin_data["liquidity"] < MIN_LIQUIDITY: return None
    if not (ATH_DROP_RANGE[0] <= coin_data["ath_drop"] <= ATH_DROP_RANGE[1]): return None
    if not coin_data["is_safe"]: return None
    
    # 2. Technical Filter (Zon Reset & Golden Pocket)
    if coin_data["rsi"] > RSI_RESET_ZONE: return None
    if not coin_data["fibo_hit"]: return None
    
    # 3. Smart Money Filter (Net-Flow USD)
    if coin_data["net_flow_usd_15m"] > (coin_data["net_flow_out_15m"] * 2): 
        return "STRONG BUY"
    elif coin_data["net_flow_usd_15m"] > coin_data["net_flow_out_15m"]:
        return "ACCUMULATE"
    else:
        return "HIGH RISK" # Akan ditelan oleh Penapis Bayang

# =====================================================================
# MODUL 4: PEMANCAR TELEGRAM & SHADOW FILTER
# =====================================================================
def send_vip_signal(coin_data, verdict):
    global signal_found_this_cycle
    
    # SHADOW FILTER: Telan amaran High Risk
    if verdict == "HIGH RISK":
        logging.info("Shadow Filter aktif. Amaran High Risk disekat.")
        return

    color = "🟢" if verdict == "STRONG BUY" else "🟡"
    reason = "Golden Pocket & Smart Money agresif" if verdict == "STRONG BUY" else "Golden Pocket & pengumpulan berperingkat"
    
    # Mesej Mockup VVIP (Data statik untuk kerangka, akan diganti pembolehubah dinamik)
    msg = f"""🌟 *NARRATIVE ALERT: LIQUID-RESTAKING-TOKENS*

*Asset Identified:* Pendle `$PENDLE`
`0x808507121B80c02388fEd11B37812B429A440D9E`

📊 *MARKET AGGREGATE*
   *Price* : `$5.45` | *Rank* : `#85`
   *Drop 24H* : `-2.10% 🩸` | *ATH Drop* : `-45.00% 📉`

📈 *TECHNICAL INTEL*
   *Trend* : RSI: Zon Reset 🟢 | MACD: Bullish 🟢
   *Momentum* : VOL: Signifikan 🟢
   *Pullback* : Fibo (0.618) 🎯

🌊 *MARKET SENTIMENT*
   *Order Flow* : {verdict} {color} ($350k In / $45k Out)
   *Social Hype*: VIRAL 🔥 (Twitter)

⛓️ *ON-CHAIN SECURITY*
   *Network* : *ETHEREUM* | *Liquidity*: `$1,200,000` 🟢
   *Security* : ✅ SAFE (Score: 100)

⚡ *VERDICT : {color} {verdict}*
   _{reason}_

[ 🦄 Maestro ] [ 🤖 Analysis (VIP) ]
[ 🟨 Binance ] [ 📰 Berita X ]
[ 🐦 Twitter ] [ ✈️ Telegram ] [ 🌐 Website ]
[ 🦎 CoinGecko ] [ 📊 Dexscreener ]
"""
    try:
        bot.send_message(VIP_CHANNEL_ID, msg, parse_mode="Markdown", disable_web_page_preview=True)
        signal_found_this_cycle = True
        logging.info("Signal VIP berjaya dihantar.")
    except Exception as e:
        logging.error(f"Ralat hantar signal: {e}")

# =====================================================================
# MODUL 5: MARKET PULSE (HEARTBEAT)
# =====================================================================
def send_market_pulse():
    global signal_found_this_cycle
    
    if not signal_found_this_cycle:
        msg = (
            "🟢 *SYSTEM HEARTBEAT : ACTIVE*\n\n"
            "📡 *Status:* AlphaV3 memantau aset merentas sektor berprestasi tinggi.\n"
            "📊 *Pemerhatian:* Pasaran sedang agresif. Tiada aset berada di paras _Golden Pocket_ buat masa ini."
        )
        try:
            bot.send_message(VIP_CHANNEL_ID, msg, parse_mode="Markdown")
            logging.info("Market Pulse dihantar.")
        except Exception as e:
            logging.error(f"Ralat hantar Market Pulse: {e}")
            
    signal_found_this_cycle = False

# =====================================================================
# RUTIN UTAMA (MAIN ENGINE LOOP)
# =====================================================================
def alpha_v3_job():
    logging.info("Memulakan Kitaran Imbasan AlphaV3...")
    engine_one_core_scan()
    time.sleep(5)
    engine_two_satellite_scan()
    logging.info("Kitaran selesai. Menunggu pusingan seterusnya.")

if __name__ == "__main__":
    # 1. Hidupkan Dummy Web Server untuk bypass Render
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    logging.info("Dummy Web Server diaktifkan (Render Bypass Active).")

    # 2. Hantar amaran Auto-Boot ke Admin
    time.sleep(2) # Beri masa untuk pelayan stabil
    send_admin_reboot_alert()
    
    # 3. Penjadualan Kitaran (Schedule)
    schedule.every(15).minutes.do(alpha_v3_job) 
    schedule.every(6).hours.do(send_market_pulse) 
    
    logging.info("Radar AlphaV3 kini aktif sepenuhnya. Menunggu...")
    
    # 4. Loop Skrip Utama
    while True:
        schedule.run_pending()
        time.sleep(1)
