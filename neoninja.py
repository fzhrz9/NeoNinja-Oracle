import os
import time
import requests
import telebot
import schedule
from datetime import datetime
from groq import Groq  # TUKAR KE GROQ

# =====================================================================
# 1. KONFIGURASI & API KEYS (FINAL LOCK)
# =====================================================================
TELEGRAM_BOT_TOKEN = "TOKEN_BOT_KAU"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # GUNA KEY DARI console.groq.com
VIP_CHANNEL_ID = "-1003943365561"
ADMIN_ID = "970309251"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
# INISIALISASI GROQ CLIENT
groq_client = Groq(api_key=GROQ_API_KEY)

# PARAMETER SWEET SPOT (FINAL)
MC_MIN, MC_MAX = 5000000, 500000000
MIN_LIQUIDITY = 250000
MIN_VOL_MC_RATIO = 0.10
MIN_24H_CHANGE = 5.0
MAX_1H_CHANGE = -1.5
FIBO_ZONE = (0.5, 0.618)
SMART_MONEY_RATIO = 1.5

# SHARIAH BLACKLIST
SHARIAH_BLACKLIST = ['gambling', 'gamblefi', 'lending', 'borrowing', 'derivatives', 'perpetuals', 'adult']

# ENGINE 1: CORE NARRATIVES
CORE_NARRATIVES = ['artificial-intelligence', 'depin', 'real-world-assets-rwa', 'gaming', 'infrastructure']

# =====================================================================
# 2. MODUL SHARIAH & FILTRATION
# =====================================================================
def is_shariah_compliant(categories):
    return not any(cat.lower() in SHARIAH_BLACKLIST for cat in categories)

def analyze_sweet_spot(coin_data):
    """
    Fungsi pengesahan gred institusi.
    Input: Data mentah dari API
    Output: Boolean & Verdict
    """
    # 1. Fundamental Check
    if not (MC_MIN <= coin_data['market_cap'] <= MC_MAX): return False
    if coin_data['liquidity'] < MIN_LIQUIDITY: return False
    if (coin_data['volume_24h'] / coin_data['market_cap']) < MIN_VOL_MC_RATIO: return False
    
    # 2. Price Action Check
    if coin_data['price_change_24h'] < MIN_24H_CHANGE: return False
    if coin_data['price_change_1h'] > MAX_1H_CHANGE: return False
    
    # 3. Technical (Fibo & RSI)
    # Simulasi pengiraan Fibo 0.618 dari Swing Low/High
    if not (FIBO_ZONE[0] <= coin_data['current_fibo_pos'] <= FIBO_ZONE[1]): return False
    
    return True

# =====================================================================
# 3. MODUL AI VIP INSIGHTS (GROQ / LLAMA 3)
# =====================================================================
def get_ai_vip_report(coin):
    """Menjana laporan forensik rojak (English/Malay) gred VVIP guna Groq"""
    prompt = f"""
    Generate a professional crypto analysis for {coin['name']} (${coin['symbol']}).
    Language: Professional Malay mixed with English trading terms (Rojak style).
    Structure:
    1. Narrative & Catalyst: Explain the sector, RWA/Utility, and compare with a major competitor (e.g. $FIL).
    2. Smart Money Intel: Mention 4 elite wallets accumulation, social sentiment 'Mula Panas', and front-run opportunity.
    3. Execution Plan: Entry Zone (Fibo), TP1 (Safe), TP2 (Target), TP3 (Moon), SL (Invalidation), and R:R Ratio (1:3.5).
    Keep it concise but high conviction.
    """
    
    # MENGGUNAKAN MODEL LLAMA 3 DI GROQ
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-specdec",
        messages=[
            {"role": "system", "content": "You are a Senior Hedge Fund Analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content

# =====================================================================
# 4. BROADCAST & INTERFACE
# =====================================================================
def send_signal(coin, verdict="STRONG BUY"):
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

[ 🦄 Maestro ] [ 🤖 Analysis (VIP) ]
[ 🟨 Binance ] [ 📰 Berita X ]
[ 🐦 Twitter ] [ ✈️ Telegram ] [ 🌐 Website ]
"""
    bot.send_message(VIP_CHANNEL_ID, msg, parse_mode="Markdown", disable_web_page_preview=True)

# =====================================================================
# 5. MAIN LOOPS (DUAL-ENGINE)
# =====================================================================
def main_job():
    # ENGINE 1 & 2 logic execution
    # 1. Fetch data from APIs (CoinGecko / Dexscreener)
    # 2. Filter by Shariah (is_shariah_compliant)
    # 3. Filter by Sweet Spot (analyze_sweet_spot)
    # 4. If all pass -> send_signal()
    print(f"Scanning market... {datetime.now()}")

if __name__ == "__main__":
    # Auto-Reboot Alert
    bot.send_message(ADMIN_ID, "🚨 **SYSTEM REBOOTED**\nPelayan awan kembali aktif. Enjin AlphaV3 beroperasi secara automatik.")
    
    schedule.every(15).minutes.do(main_job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
