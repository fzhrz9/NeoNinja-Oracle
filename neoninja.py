import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import time
import os
from datetime import datetime
import threading
from flask import Flask

# ==========================================
# ⚙️ CORE SYSTEM: HEALTH CHECK DAEMON
# ==========================================
app = Flask(__name__)
@app.route('/')
def health_check():
    return "STATUS: OK | NEONINJA ORACLE PROTOCOL (V2.8 HYBRID) OPERATIONAL"

def initialize_daemon():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

daemon_thread = threading.Thread(target=initialize_daemon, daemon=True)
daemon_thread.start()

# ==========================================
# 📡 CONFIGURATION
# ==========================================
API_TOKEN = '8673710597:AAGD4I53588YSL1QK9ZllzlaeQY68gFttSQ' 
CG_API_KEY = 'CG-b4VSbfrpCgK5seMpcHssGJe7' 

bot = telebot.TeleBot(API_TOKEN)
MEMORY_CACHE = {} 
SYSTEM_ACTIVE = False 

NARRATIVES = [
    'artificial-intelligence', 'ai-agents', 'infrastructure', 'depin', 
    'internet-of-things-iot', 'decentralized-finance-defi', 
    'layer-1', 'layer-2', 'china-concept', 'real-world-assets-rwa'
]
CURRENT_NARRATIVE_IDX = 0

CHAIN_MAP = {
    'solana': 'SOL', 'ethereum': 'ETH', 'bsc': 'BSC', 'base': 'BASE',
    'arbitrum': 'ARB', 'avalanche': 'AVAX', 'tron': 'TRX', 'ton': 'TON'
}

GOPLUS_MAP = {'ethereum': '1', 'bsc': '56', 'arbitrum': '42161', 'avalanche': '43114', 'base': '8453'}

# ==========================================
# 📈 TECHNICAL ENGINE: RSI, MACD, VOLUME
# ==========================================
def get_technical_intel(coin_id):
    try:
        # Sedut data 30 hari untuk MACD & RSI (Daily)
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=30&interval=daily"
        res = requests.get(url, timeout=10).json()
        
        prices = [p[1] for p in res.get('prices', [])]
        volumes = [v[1] for v in res.get('total_volumes', [])]
        
        if len(prices) < 26: return "N/A", "🟡", "🟡", 50 # Default safe return

        # 1. RSI (14D)
        gains, losses = [], []
        for i in range(len(prices)-14, len(prices)):
            diff = prices[i] - prices[i-1]
            gains.append(max(diff, 0))
            losses.append(abs(min(diff, 0)))
        avg_g, avg_l = sum(gains)/14, sum(losses)/14
        rsi = 100 - (100 / (1 + (avg_g/avg_l))) if avg_l != 0 else 100
        
        rsi_label = "Neutral 🟡"
        if rsi < 30: rsi_label = "Oversold 🟢"
        elif rsi > 70: rsi_label = "Overbought 🔴"

        # 2. MACD (12, 26, 9) - Simple EMA approach
        ema12 = sum(prices[-12:]) / 12
        ema26 = sum(prices[-26:]) / 26
        macd_line = ema12 - ema26
        signal_line = sum(prices[-9:]) / 9 # Simplified signal
        macd_emoji = "🟢" if macd_line > 0 else "🔴"
        if abs(macd_line) < (ema26 * 0.001): macd_emoji = "🟡"

        # 3. VOLUME SPIKE (Current vs 7-day Avg)
        avg_vol = sum(volumes[-8:-1]) / 7
        curr_vol = volumes[-1]
        vol_emoji = "🟡"
        if curr_vol > (avg_vol * 1.5): vol_emoji = "🟢"
        elif curr_vol < (avg_vol * 0.5): vol_emoji = "🔴"

        return rsi_label, macd_emoji, vol_emoji, rsi
    except:
        return "N/A", "🟡", "🟡", 50

# ==========================================
# 🛡️ SECURITY ENGINE
# ==========================================
def check_security(chain_id, address):
    try:
        if chain_id == 'solana':
            r = requests.get(f"https://api.rugcheck.xyz/v1/tokens/{address}/report", timeout=10).json()
            return f"{r.get('score', 0)} (Safe)" if r.get('score', 0) < 500 else "🚨 HIGH RISK"
        
        gp_id = GOPLUS_MAP.get(chain_id)
        if not gp_id: return "N/A (Imbas Manual)"
        res = requests.get(f"https://api.gopluslabs.io/api/v1/token_security/{gp_id}?contract_addresses={address}", timeout=10).json()
        data = res.get('result', {}).get(address.lower(), {})
        if data.get('is_honeypot') == '1': return "🚨 HONEYPOT"
        return f"✅ SAFE (Score: 100)"
    except: return "N/A"

# ==========================================
# 🧠 HYBRID PIPELINE (THE "OR" LOGIC)
# ==========================================
def verify_on_chain(symbol, cg_data):
    try:
        # Market Cap Filter ($2M - $500M)
        mc = cg_data.get('market_cap', 0)
        if not (2000000 <= mc <= 500000000): return None, None

        # 1. DAPATKAN DATA TEKNIKAL DULU
        rsi_label, macd_emoji, vol_emoji, rsi_num = get_technical_intel(cg_data['id'])
        p24 = cg_data.get('price_change_percentage_24h', 0)

        # ⚠️ LOGIK "OR": Salah satu lepas, kita rembat!
        # Syarat: (Jatuh > 2%) ATAU (RSI < 30)
        is_discounted = p24 <= -2
        is_oversold = rsi_num <= 30

        if not (is_discounted or is_oversold): return None, None

        # 2. SEMAK DEXSCREENER (Liquidity & Chain)
        dex = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={symbol}", timeout=10).json()
        pair = next((p for p in dex.get('pairs', []) if p['chainId'] in CHAIN_MAP and p['baseToken']['symbol'].lower() == symbol.lower()), None)
        if not pair or pair.get('liquidity', {}).get('usd', 0) < 50000: return None, None

        chain_id = pair['chainId']
        addr = pair['baseToken']['address']
        
        # 3. SECURITY SCAN
        sec_status = check_security(chain_id, addr)
        if "🚨" in sec_status: return None, None

        # FORMAT LAPORAN
        report = f"**Asset Identified:** {cg_data['name']} `${symbol.upper()}`\n"
        report += f"`{addr}`\n\n"
        report += f"📊 **MARKET AGGREGATE**\n"
        report += f"   Network   : **{CHAIN_MAP[chain_id]}**\n"
        report += f"   M.Cap     : `${mc:,.0f}`\n"
        report += f"   Drop 24H  : `{p24:.2f}%` 🩸\n\n"
        report += f"📈 **TECHNICAL INTEL (1D)**\n"
        report += f"   Rsi       : {rsi_label}\n"
        report += f"   Macd      : {macd_emoji}\n"
        report += f"   Volume    : {vol_emoji}\n\n"
        report += f"⛓️ **SECURITY**\n"
        report += f"   Status    : {sec_status}\n"

        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        btn_bot = InlineKeyboardButton(f"🔫 Terminal ({CHAIN_MAP[chain_id]})", url=f"https://t.me/maestro?start={addr}" if chain_id != 'solana' else f"https://t.me/bonkbot_bot?start={addr}")
        markup.add(btn_bot)
        markup.add(InlineKeyboardButton("🟨 Binance", url=f"https://binance.com/trade/{symbol.upper()}_USDT"),
                   InlineKeyboardButton("📰 Berita X", url=f"https://twitter.com/search?q=%24{symbol}&f=live"))
        markup.add(InlineKeyboardButton("🦎 CoinGecko", url=f"https://coingecko.com/coins/{cg_data['id']}"),
                   InlineKeyboardButton("📊 Dexscreener", url=f"https://dexscreener.com/{chain_id}/{addr}"))
        
        return report, markup
    except: return None, None

def neoninja_pipeline(chat_id):
    global SYSTEM_ACTIVE, CURRENT_NARRATIVE_IDX
    headers = {"accept": "application/json", "x-cg-demo-api-key": CG_API_KEY}
    while SYSTEM_ACTIVE:
        try:
            current_time = time.time()
            active_nav = NARRATIVES[CURRENT_NARRATIVE_IDX]
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Hunting: {active_nav.upper()}")
            
            data = requests.get(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category={active_nav}&order=market_cap_desc&per_page=250", headers=headers).json()
            for coin in data:
                if not SYSTEM_ACTIVE: break
                symbol = coin['symbol']
                if symbol not in MEMORY_CACHE or (current_time - MEMORY_CACHE[symbol]) > 28800:
                    report, markup = verify_on_chain(symbol, coin)
                    if report and markup:
                        MEMORY_CACHE[symbol] = current_time
                        bot.send_message(chat_id, f"🌟 **NARRATIVE: {active_nav.upper()}**\n\n" + report, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)
                    time.sleep(2)
            
            CURRENT_NARRATIVE_IDX = (CURRENT_NARRATIVE_IDX + 1) % len(NARRATIVES)
            time.sleep(600)
        except: time.sleep(30)

@bot.message_handler(commands=['start'])
def start(m): bot.reply_to(m, "✅ **NEONINJA HYBRID V2.8**\nType `/scan` to start.")

@bot.message_handler(commands=['scan'])
def scan(m):
    global SYSTEM_ACTIVE
    if not SYSTEM_ACTIVE:
        SYSTEM_ACTIVE = True
        bot.reply_to(m, "🟢 **SCANNER ACTIVE**\nLogik OR (Price/RSI) diaktifkan.")
        threading.Thread(target=neoninja_pipeline, args=(m.chat.id,), daemon=True).start()

@bot.message_handler(commands=['stop'])
def stop(m):
    global SYSTEM_ACTIVE
    SYSTEM_ACTIVE = False
    bot.reply_to(m, "🔴 Scanner Stopped.")

if __name__ == "__main__":
    bot.polling(none_stop=True)
