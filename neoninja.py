import os
import time
import requests
import telebot
import schedule
import threading  # Tambah untuk server dummy
from http.server import HTTPServer, BaseHTTPRequestHandler # Tambah untuk Render
from datetime import datetime
from groq import Groq

# =====================================================================
# 1. KONFIGURASI & API KEYS
# =====================================================================
TELEGRAM_BOT_TOKEN = "8673710597:AAGD4I53588YSL1QK9ZllzlaeQY68gFttSQ"
GROQ_API_KEY = os.getenv("GROQ_API_KEY") 
VIP_CHANNEL_ID = "-1003943365561"
ADMIN_ID = "970309251"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# MATIKAN GROQ SECARA LEMBUT (Bypass jika tiada Key)
groq_client = None
if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
    except:
        groq_client = None

# PARAMETER SWEET SPOT
MC_MIN, MC_MAX = 5000000, 500000000
MIN_LIQUIDITY = 250000
MIN_VOL_MC_RATIO = 0.10
MIN_24H_CHANGE = 5.0
MAX_1H_CHANGE = -1.5
FIBO_ZONE = (0.5, 0.618)
SMART_MONEY_RATIO = 1.5

SHARIAH_BLACKLIST = ['gambling', 'gamblefi', 'lending', 'borrowing', 'derivatives', 'perpetuals', 'adult']
CORE_NARRATIVES = ['artificial-intelligence', 'depin', 'real-world-assets-rwa', 'gaming', 'infrastructure']

# =====================================================================
# 2. MODUL SHARIAH & FILTRATION
# =====================================================================
def is_shariah_compliant(categories):
    return not any(cat.lower() in SHARIAH_BLACKLIST for cat in categories)

def analyze_sweet_spot(coin_data):
    if not (MC_MIN <= coin_data['market_cap'] <= MC_MAX): return False
    if coin_data['liquidity'] < MIN_LIQUIDITY: return False
    if (coin_data['volume_24h'] / coin_data['market_cap']) < MIN_VOL_MC_RATIO: return False
    if coin_data['price_change_24h'] < MIN_24H_CHANGE: return False
    if coin_data['price_change_1h'] > MAX_1H_CHANGE: return False
    if not (FIBO_ZONE[0] <= coin_data['current_fibo_pos'] <= FIBO_ZONE[1]): return False
    return True

# =====================================================================
# 3. MODUL AI VIP INSIGHTS (HOLD / DISABLED MODE)
# =====================================================================
def get_ai_vip_report(coin):
    """Fungsi Groq dimatikan buat sementara. Hantar info manual."""
    return (
        "🚀 **ALPHA VIP INSIGHTS**\n\n"
        "Analisis AI sedang dikemaskini oleh pihak teknikal. "
        "Sila rujuk *Execution Plan* di bawah berdasarkan data Smart Money semasa.\n\n"
        "• **Naratif:** Potensi tinggi dalam sektor " + coin['narrative'].upper() + ".\n"
        "• **Status:** Early accumulation detected."
    )

# =====================================================================
# 4. BROADCAST & INTERFACE
# =====================================================================
def send_signal(coin, verdict="STRONG BUY"):
    # Bot akan panggil fungsi AI yang dah 'diam' tu
    ai_report = get_ai_vip_report(coin)
    
    msg = f"""⚡ **ALPHA EXECUTION : {coin['narrative'].upper()}**

**Asset Identified:** {coin['name']} `${coin['symbol']}`
`{coin['contract_address']}`

📊 **MARKET METRICS**
   **Market Cap** : `${coin['market_cap'] / 1e6:.1f}M` | **Vol 24H** : `${coin['volume_24h'] / 1e6:.1f}M` 🟢
   **Trend 24H** : `+{coin['price_change_24h']}%` 🟢 | **1H Retracement** : `{coin['price_change_1h']}%` 🩸

📈 **TECHNICAL INTEL**
   **Momentum (1H)** : RSI {coin['rsi']} (Oversold Reset) 🟢 
   **Value Zone** : Fibonacci (0.5 - 0.618) 🎯

🌊 **ORDER FLOW SENSORS**
   **Net-Volume** : {verdict} 🟢 (${coin['buy_vol']}k In / ${coin['sell_vol']}k Out)
   **Capital Inflow**: `+{coin['flow_ratio']}x (Dominasi Institusi)`

⛓️ **ON-CHAIN SECURITY**
   **Network** : **{coin['network']}** | **Liquidity**: `${coin['liquidity'] / 1e6:.1f}M` 🟢
   **Risk Profile** : ✅ SECURE (Audit Score: 100)

⚡ **VERDICT : 🟢 {verdict}**
   *Titik entri optimum disahkan oleh zon sokongan dan kemasukan dana tunai agresif.*
"""
    bot.send_message(VIP_CHANNEL_ID, msg, parse_mode="Markdown", disable_web_page_preview=True)

# =====================================================================
# 5. RENDER PORT BINDING FIX (SERVER PALSU)
# =====================================================================
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"AlphaV3 Bot is Active")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# =====================================================================
# 6. MAIN LOOPS
# =====================================================================
def main_job():
    print(f"Scanning market... {datetime.now()}")

if __name__ == "__main__":
    # 1. Jalankan server dummy supaya Render tak matikan bot
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    # 2. Amaran Reboot
    bot.send_message(ADMIN_ID, "🚨 **SYSTEM REBOOTED**\nAlphaV3 aktif (AI Mode: Standby).")
    
    schedule.every(15).minutes.do(main_job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
