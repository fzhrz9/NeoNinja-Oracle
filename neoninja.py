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
    return "STATUS: OK | NEONINJA ORACLE PROTOCOL (V3.0 TRUE FIBO) OPERATIONAL"

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
# 📈 TECHNICAL ENGINE (RSI, MACD, VOL, TRUE FIBO)
# ==========================================
def get_technical_intel(coin_id, current_price):
    try:
        headers = {"accept": "application/json", "x-cg-demo-api-key": CG_API_KEY}
        
        # SEDUT DATA HARIAN (30 HARI)
        url_daily = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=30&interval=daily"
        res_daily = requests.get(url_daily, headers=headers, timeout=10).json()
        
        prices = [p[1] for p in res_daily.get('prices', [])]
        volumes = [v[1] for v in res_daily.get('total_volumes', [])]
        
        rsi_label, rsi_val = "Neutral 🟡", 50
        macd_emoji = "🟡"
        vol_emoji = "🟡"
        pullback_1d_hit = False
        pullback_1w_hit = False
        
        if len(prices) >= 26:
            # RSI 14D
            gains, losses = [], []
            for i in range(len(prices)-14, len(prices)):
                diff = prices[i] - prices[i-1]
                gains.append(max(diff, 0)); losses.append(abs(min(diff, 0)))
            avg_g, avg_l = sum(gains)/14, sum(losses)/14
            rsi_val = 100 - (100 / (1 + (avg_g/avg_l))) if avg_l != 0 else 100
            
            if rsi_val < 30: rsi_label = "Oversold 🟢"
            elif rsi_val > 70: rsi_label = "Overbought 🔴"

            # MACD
            ema12 = sum(prices[-12:]) / 12
            ema26 = sum(prices[-26:]) / 26
            macd_line = ema12 - ema26
            macd_emoji = "🟢" if macd_line > 0 else "🔴"
            if abs(macd_line) < (ema26 * 0.001): macd_emoji = "🟡"

            # VOLUME
            avg_vol = sum(volumes[-8:-1]) / 7
            curr_vol = volumes[-1]
            if curr_vol > (avg_vol * 1.5): vol_emoji = "🟢"
            elif curr_vol < (avg_vol * 0.5): vol_emoji = "🔴"

            # TRUE FIBO 0.50 PULLBACK (7D & 30D Swing)
            tolerance = 0.025 # 2.5% zon toleransi pantulan
            
            # Micro Swing (7 Hari / Dilabel 1D untuk UI)
            prices_7d = prices[-7:]
            fib_7d = (max(prices_7d) + min(prices_7d)) / 2
            if abs(current_price - fib_7d) / fib_7d <= tolerance: pullback_1d_hit = True
            
            # Macro Swing (30 Hari / Dilabel 1W untuk UI)
            fib_30d = (max(prices) + min(prices)) / 2
            if abs(current_price - fib_30d) / fib_30d <= tolerance: pullback_1w_hit = True

        emo_1d = "🎯" if pullback_1d_hit else "⚪"
        emo_1w = "🎯" if pullback_1w_hit else "⚪"

        return rsi_label, macd_emoji, vol_emoji, rsi_val, pullback_1d_hit, pullback_1w_hit, emo_1d, emo_1w
    except Exception as e:
        return "N/A", "🟡", "🟡", 50, False, False, "⚪", "⚪"

# ==========================================
# 🛡️ SECURITY ENGINE
# ==========================================
def check_security(chain_id, address):
    try:
        if chain_id == 'solana':
            r = requests.get(f"https://api.rugcheck.xyz/v1/tokens/{address}/report", timeout=10).json()
            return f"{r.get('score', 0)} (Safe)", r.get('score', 0) < 500
        
        gp_id = GOPLUS_MAP.get(chain_id)
        if not gp_id: return "N/A (Imbas Manual)", True
        res = requests.get(f"https://api.gopluslabs.io/api/v1/token_security/{gp_id}?contract_addresses={address}", timeout=10).json()
        data = res.get('result', {}).get(address.lower(), {})
        if data.get('is_honeypot') == '1': return "🚨 HONEYPOT", False
        return f"✅ SAFE (Score: 100)", True
    except: return "N/A", True

# ==========================================
# 🧠 HYBRID PIPELINE (AND / OR LOGIC)
# ==========================================
def verify_on_chain(symbol, cg_data):
    try:
        # [WAJIB] Market Cap ($2M - $500M)
        mc = cg_data.get('market_cap', 0)
        if not (2000000 <= mc <= 500000000): return None, None

        current_price = cg_data.get('current_price', 0)
        p24 = cg_data.get('price_change_percentage_24h', 0)

        # 1. DAPATKAN DATA TEKNIKAL & FIBO
        rsi_label, macd_emoji, vol_emoji, rsi_val, is_1d_hit, is_1w_hit, emo_1d, emo_1w = get_technical_intel(cg_data['id'], current_price)

        # [PENCETUS / OR LOGIC] - Mesti lulus salah satu
        is_discounted = p24 <= -2
        is_oversold = rsi_val < 30
        
        if not (is_discounted or is_oversold or is_1d_hit or is_1w_hit): return None, None

        # [WAJIB] Semak Dexscreener (Liquidity > $50k & Volume > $20k)
        dex = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={symbol}", timeout=10).json()
        pair = next((p for p in dex.get('pairs', []) if p['chainId'] in CHAIN_MAP and p['baseToken']['symbol'].lower() == symbol.lower()), None)
        
        if not pair: return None, None
        liq = pair.get('liquidity', {}).get('usd', 0)
        vol24 = pair.get('volume', {}).get('h24', 0)
        
        if liq < 50000 or vol24 < 20000: return None, None

        chain_id = pair['chainId']
        addr = pair['baseToken']['address']
        
        # [WAJIB] Security Scan
        sec_text, is_safe = check_security(chain_id, addr)
        if not is_safe: return None, None

        rank = cg_data.get('market_cap_rank', 'N/A')
        ath = cg_data.get('ath_change_percentage', 0)

        # FORMAT LAPORAN (UI V2.9 MOCKUP)
        report = f"**Asset Identified:** {cg_data['name']} `${symbol.upper()}`\n"
        report += f"`{addr}`\n\n"
        
        report += f"📊 **MARKET AGGREGATE**\n"
        report += f"   Network      : **{CHAIN_MAP[chain_id]}**\n"
        report += f"   Price        : `${current_price}`\n"
        report += f"   Global Rank  : `#{rank}`\n"
        report += f"   Market Cap   : `${mc:,.0f}`\n"
        report += f"   Diskaun 24H  : `{p24:.2f}%` 🩸\n"
        report += f"   Diskaun ATH  : `{ath:.2f}%` 📉\n\n"
        
        report += f"📈 **TECHNICAL INTEL (1D)**\n"
        report += f"   Trend        : RSI: {rsi_label} | MACD: {macd_emoji}\n"
        report += f"   Momentum     : VOL: {vol_emoji} | Pullback 50%: 1D {emo_1d} | 1W {emo_1w}\n\n"
        
        report += f"⛓️ **ON-CHAIN SECURITY**\n"
        report += f"   Liquidity    : `${liq:,.0f}` 🟢\n"
        report += f"   Security     : {sec_text}\n"

        # BINA BUTANG
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        
        btn_bot = InlineKeyboardButton(f"🔫 Beli di BonkBot ({CHAIN_MAP[chain_id]})" if chain_id == 'solana' else f"🦄 Beli di Maestro ({CHAIN_MAP[chain_id]})", url=f"https://t.me/bonkbot_bot?start={addr}" if chain_id == 'solana' else f"https://t.me/maestro?start={addr}")
        markup.add(btn_bot)
        
        markup.add(InlineKeyboardButton("🟨 Beli di Binance", url=f"https://binance.com/trade/{symbol.upper()}_USDT"),
                   InlineKeyboardButton("📰 Radar Berita (X)", url=f"https://twitter.com/search?q=%24{symbol}&f=live"))
        
        socials = pair.get('info', {}).get('socials', [])
        tw_url = next((s['url'] for s in socials if s['type'] == 'twitter'), None)
        tg_url = next((s['url'] for s in socials if s['type'] == 'telegram'), None)
        web_url = pair.get('info', {}).get('websites', [{'url': None}])[0]['url'] if pair.get('info', {}).get('websites') else None
        
        soc = []
        if tw_url: soc.append(InlineKeyboardButton("🐦 Twitter", url=tw_url))
        if tg_url: soc.append(InlineKeyboardButton("✈️ Telegram", url=tg_url))
        if web_url: soc.append(InlineKeyboardButton("🌐 Website", url=web_url))
        if soc: markup.add(*soc)
        
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
            
            data = requests.get(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category={active_nav}&order=market_cap_desc&per_page=250", headers=headers, timeout=15).json()
            for coin in data:
                if not SYSTEM_ACTIVE: break
                symbol = coin['symbol']
                if symbol not in MEMORY_CACHE or (current_time - MEMORY_CACHE[symbol]) > 28800:
                    report, markup = verify_on_chain(symbol, coin)
                    if report and markup:
                        MEMORY_CACHE[symbol] = current_time
                        bot.send_message(chat_id, f"🌟 **NARRATIVE ALERT: {active_nav.upper()}**\n\n" + report, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)
                    time.sleep(2.5)
            
            CURRENT_NARRATIVE_IDX = (CURRENT_NARRATIVE_IDX + 1) % len(NARRATIVES)
            time.sleep(600)
        except Exception as e:
            print(f"Error Pipeline: {e}")
            time.sleep(30)

@bot.message_handler(commands=['start'])
def start(m): bot.reply_to(m, "✅ **NEONINJA TRUE FIBO V3.0**\nType `/scan` to start.")

@bot.message_handler(commands=['scan'])
def scan(m):
    global SYSTEM_ACTIVE
    if not SYSTEM_ACTIVE:
        SYSTEM_ACTIVE = True
        bot.reply_to(m, "🟢 **V3.0 SCANNER ACTIVE**\nLogik AND/OR (True Fibo Swing) & Security berjalan.")
        threading.Thread(target=neoninja_pipeline, args=(m.chat.id,), daemon=True).start()

@bot.message_handler(commands=['stop'])
def stop(m):
    global SYSTEM_ACTIVE
    SYSTEM_ACTIVE = False
    bot.reply_to(m, "🔴 Scanner Stopped.")

if __name__ == "__main__":
    bot.polling(none_stop=True)
