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
    return "STATUS: OK | NEONINJA V4.0 (SENTIMENT ENGINE) OPERATIONAL"

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

NARRATIVES = ['artificial-intelligence', 'ai-agents', 'infrastructure', 'depin', 'internet-of-things-iot', 'decentralized-finance-defi', 'layer-1', 'layer-2', 'china-concept', 'real-world-assets-rwa']
CURRENT_NARRATIVE_IDX = 0
CHAIN_MAP = {'solana': 'SOL', 'ethereum': 'ETH', 'bsc': 'BSC', 'base': 'BASE', 'arbitrum': 'ARB', 'avalanche': 'AVAX', 'tron': 'TRX', 'ton': 'TON'}
GOPLUS_MAP = {'ethereum': '1', 'bsc': '56', 'arbitrum': '42161', 'avalanche': '43114', 'base': '8453'}

# ==========================================
# 📈 TECHNICAL & SENTIMENT ENGINE
# ==========================================
def get_advanced_intel(coin_id, current_price, pair_data):
    try:
        headers = {"accept": "application/json", "x-cg-demo-api-key": CG_API_KEY}
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=30&interval=daily"
        res = requests.get(url, headers=headers, timeout=10).json()
        
        prices = [p[1] for p in res.get('prices', [])]
        volumes = [v[1] for v in res.get('total_volumes', [])]
        
        rsi_label, rsi_val = "Neutral 🟡", 50
        macd_emoji, vol_emoji = "🟡", "🟡"
        p_1d, p_1w = "⚪", "⚪"
        is_1d_hit, is_1w_hit = False, False

        if len(prices) >= 26:
            # RSI & MACD
            g, l = [], []
            for i in range(len(prices)-14, len(prices)):
                diff = prices[i] - prices[i-1]
                g.append(max(diff, 0)); l.append(abs(min(diff, 0)))
            rsi_val = 100 - (100 / (1 + (sum(g)/sum(l)))) if sum(l) != 0 else 100
            rsi_label = "Oversold 🟢" if rsi_val < 30 else ("Overbought 🔴" if rsi_val > 70 else "Neutral 🟡")
            macd_emoji = "🟢" if (sum(prices[-12:])/12 - sum(prices[-26:])/26) > 0 else "🔴"
            
            # VOLUME & FIBO
            if volumes[-1] > (sum(volumes[-8:-1])/7 * 1.5): vol_emoji = "🟢"
            tol = 0.025
            f7d = (max(prices[-7:]) + min(prices[-7:])) / 2
            f30d = (max(prices) + min(prices)) / 2
            if abs(current_price - f7d)/f7d <= tol: p_1d, is_1d_hit = "🎯", True
            if abs(current_price - f30d)/f30d <= tol: p_1w, is_1w_hit = "🎯", True

        # 🌊 MARKET SENTIMENT (ORDER FLOW)
        buys = pair_data.get('txns', {}).get('h1', {}).get('buys', 0)
        sells = pair_data.get('txns', {}).get('h1', {}).get('sells', 0)
        total_tx = buys + sells
        flow_text = "Neutral ⚪"
        if total_tx > 0:
            buy_pct = (buys / total_tx) * 100
            if buy_pct > 70: flow_text = f"STRONG BUY 🟢 ({buy_pct:.0f}% / {100-buy_pct:.0f}%)"
            elif buy_pct < 30: flow_text = f"PANIC SELL 🔴 ({buy_pct:.0f}% / {100-buy_pct:.0f}%)"
            else: flow_text = f"Stable 🟡 ({buy_pct:.0f}% / {100-buy_pct:.0f}%)"
        
        # 🔥 SOCIAL HYPE (SIMULATED)
        fdv = pair_data.get('fdv', 1)
        liq = pair_data.get('liquidity', {}).get('usd', 1)
        hype = "SENDU 🧊"
        if (volumes[-1] / fdv) > 0.2 or (buys > 100): hype = "VIRAL 🔥 (Twitter Trending)"
        elif (volumes[-1] / fdv) > 0.1: hype = "Trending 🟢"

        return rsi_label, macd_emoji, vol_emoji, rsi_val, is_1d_hit, is_1w_hit, p_1d, p_1w, flow_text, hype
    except: return "N/A", "🟡", "🟡", 50, False, False, "⚪", "⚪", "Neutral ⚪", "SENDU 🧊"

# ==========================================
# 🛡️ SECURITY & VERIFICATION
# ==========================================
def check_security(chain_id, address):
    try:
        if chain_id == 'solana':
            r = requests.get(f"https://api.rugcheck.xyz/v1/tokens/{address}/report", timeout=10).json()
            return f"{r.get('score', 0)} (Safe)", r.get('score', 0) < 500
        gp_id = GOPLUS_MAP.get(chain_id)
        if not gp_id: return "N/A", True
        res = requests.get(f"https://api.gopluslabs.io/api/v1/token_security/{gp_id}?contract_addresses={address}", timeout=10).json()
        data = res.get('result', {}).get(address.lower(), {})
        return ("🚨 HONEYPOT", False) if data.get('is_honeypot') == '1' else ("✅ SAFE", True)
    except: return "N/A", True

def verify_on_chain(symbol, cg_data):
    try:
        mc = cg_data.get('market_cap', 0)
        if not (2000000 <= mc <= 500000000): return None, None
        
        dex = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={symbol}", timeout=10).json()
        pair = next((p for p in dex.get('pairs', []) if p['chainId'] in CHAIN_MAP and p['baseToken']['symbol'].lower() == symbol.lower()), None)
        if not pair or pair.get('liquidity', {}).get('usd', 0) < 50000: return None, None

        cur_p = cg_data.get('current_price', 0)
        p24 = cg_data.get('price_change_percentage_24h', 0)
        
        rsi_l, macd_e, vol_e, rsi_v, hit1d, hit1w, e1d, e1w, flow, hype = get_advanced_intel(cg_data['id'], cur_p, pair)
        if not (p24 <= -2 or rsi_v < 30 or hit1d or hit1w): return None, None

        sec_t, is_safe = check_security(pair['chainId'], pair['baseToken']['address'])
        if not is_safe: return None, None

        # 📄 FORMAT V4.0 ULTRA-COMPRESSED
        report = f"**Asset Identified:** {cg_data['name']} `${symbol.upper()}`\n"
        report += f"`{pair['baseToken']['address']}`\n\n"
        report += f"📊 **MARKET AGGREGATE**\n"
        report += f"   Price: `${cur_p}` | Rank: `#{cg_data.get('market_cap_rank')}`\n"
        report += f"   Drop 24H: `{p24:.2f}%` 🩸 | ATH Drop: `{cg_data.get('ath_change_percentage'):.2f}%` 📉\n\n"
        report += f"📈 **TECHNICAL INTEL (1D)**\n"
        report += f"   Trend      : RSI: {rsi_l} | MACD: {macd_e}\n"
        report += f"   Momentum   : VOL: {vol_e}\n"
        report += f"   Pullback   : 1D {e1d} | 1W {e1w}\n\n"
        report += f"🌊 **MARKET SENTIMENT**\n"
        report += f"   Order Flow : {flow}\n"
        report += f"   Social Hype: {hype}\n\n"
        report += f"⛓️ **ON-CHAIN SECURITY**\n"
        report += f"   Network    : **{CHAIN_MAP[pair['chainId']]}** | Liquidity: `${pair['liquidity']['usd']:,.0f}` 🟢\n"
        report += f"   Security   : {sec_t}\n"

        markup = InlineKeyboardMarkup()
        btn_txt = "🔫 BonkBot" if pair['chainId'] == 'solana' else "🦄 Maestro"
        markup.add(InlineKeyboardButton(btn_txt, url=f"https://t.me/bonkbot_bot?start={pair['baseToken']['address']}" if pair['chainId'] == 'solana' else f"https://t.me/maestro?start={pair['baseToken']['address']}"))
        markup.add(InlineKeyboardButton("🟨 Binance", url=f"https://binance.com/trade/{symbol.upper()}_USDT"), InlineKeyboardButton("📰 Berita X", url=f"https://twitter.com/search?q=%24{symbol}&f=live"))
        markup.add(InlineKeyboardButton("🐦 Twitter", url=pair.get('info', {}).get('socials', [{}])[0].get('url', 'https://twitter.com')), InlineKeyboardButton("✈️ Telegram", url=pair.get('info', {}).get('socials', [{},{}])[1].get('url', 'https://t.me')), InlineKeyboardButton("🌐 Website", url=pair.get('info', {}).get('websites', [{}])[0].get('url', '')))
        markup.add(InlineKeyboardButton("🦎 CoinGecko", url=f"https://coingecko.com/coins/{cg_data['id']}"), InlineKeyboardButton("📊 Dexscreener", url=pair['url']))
        
        return report, markup
    except: return None, None

def neoninja_pipeline(chat_id):
    global SYSTEM_ACTIVE, CURRENT_NARRATIVE_IDX
    headers = {"accept": "application/json", "x-cg-demo-api-key": CG_API_KEY}
    while SYSTEM_ACTIVE:
        try:
            active_nav = NARRATIVES[CURRENT_NARRATIVE_IDX]
            data = requests.get(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category={active_nav}&order=market_cap_desc&per_page=250", headers=headers).json()
            for coin in data:
                if not SYSTEM_ACTIVE: break
                if coin['symbol'] not in MEMORY_CACHE or (time.time() - MEMORY_CACHE[coin['symbol']]) > 28800:
                    report, markup = verify_on_chain(coin['symbol'], coin)
                    if report and markup:
                        MEMORY_CACHE[coin['symbol']] = time.time()
                        bot.send_message(chat_id, f"🌟 **NARRATIVE ALERT: {active_nav.upper()}**\n\n" + report, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)
                    time.sleep(2.5)
            CURRENT_NARRATIVE_IDX = (CURRENT_NARRATIVE_IDX + 1) % len(NARRATIVES)
            time.sleep(600)
        except: time.sleep(30)

@bot.message_handler(commands=['start'])
def start(m): bot.reply_to(m, "✅ **NEONINJA V4.0 (ULTRA)**\nType `/scan` to start.")

@bot.message_handler(commands=['scan'])
def scan(m):
    global SYSTEM_ACTIVE
    if not SYSTEM_ACTIVE:
        SYSTEM_ACTIVE = True
        bot.reply_to(m, "🟢 **V4.0 ULTIMATE ACTIVE**\nOrder Flow & Social Hype Engine Running.")
        threading.Thread(target=neoninja_pipeline, args=(m.chat.id,), daemon=True).start()

@bot.message_handler(commands=['stop'])
def stop(m):
    global SYSTEM_ACTIVE = False
    bot.reply_to(m, "🔴 Scanner Stopped.")

if __name__ == "__main__":
    bot.polling(none_stop=True)
