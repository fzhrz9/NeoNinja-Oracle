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
    return "STATUS: OK | NEONINJA ORACLE PROTOCOL (V2.1 OMNI-VERSE) OPERATIONAL"

def initialize_daemon():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

daemon_thread = threading.Thread(target=initialize_daemon, daemon=True)
daemon_thread.start()

# ==========================================
# 📡 TELEGRAM & COINGECKO API KEYS
# ==========================================
API_TOKEN = '8673710597:AAGD4I53588YSL1QK9ZllzlaeQY68gFttSQ' 
CG_API_KEY = 'CG-b4VSbfrpCgK5seMpcHssGJe7' 

bot = telebot.TeleBot(API_TOKEN)

MEMORY_CACHE = {} 
SYSTEM_ACTIVE = False 

# 🌐 KITARAN NARATIF GERGASI (10 Sektor)
NARRATIVES = [
    'artificial-intelligence', 'ai-agents', 'infrastructure', 'depin', 
    'internet-of-things-iot', 'decentralized-finance-defi', 
    'layer-1', 'layer-2', 'china-concept', 'real-world-assets-rwa'
]
CURRENT_NARRATIVE_IDX = 0

# 🗺️ PETA RANTAIAN (Selari dengan Maestro & Dexscreener)
CHAIN_MAP = {
    'solana': 'SOL',
    'ethereum': 'ETH',
    'bsc': 'BSC',
    'base': 'BASE',
    'arbitrum': 'ARB',
    'avalanche': 'AVAX',
    'tron': 'TRX',
    'ton': 'TON'
}

# ==========================================
# 🧠 ALGORITHM: OMNI-VERSE & VIP UI
# ==========================================
def verify_on_chain(symbol, cg_data):
    try:
        # Tapisan Awal CoinGecko: Market Cap $5M - $150M sahaja (Zon Mid-Cap)
        market_cap = cg_data.get('market_cap', 0)
        if not (5000000 <= market_cap <= 150000000): return None, None

        dex_search = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={symbol}", timeout=10).json()
        if not dex_search.get('pairs'): return None, None
        
        target_pair = None
        allowed_chains = list(CHAIN_MAP.keys())
        
        for pair in dex_search['pairs']:
            if pair.get('chainId') in allowed_chains and pair['baseToken']['symbol'].lower() == symbol.lower():
                target_pair = pair
                break
                
        if not target_pair: return None, None
        
        chain_id = target_pair.get('chainId')
        contract_address = target_pair['baseToken']['address']
        liquidity_usd = target_pair.get('liquidity', {}).get('usd', 0)
        volume_24h = target_pair.get('volume', {}).get('h24', 0)
        
        # ⚠️ TAPISAN GRED INSTITUSI: Minimum $100k LP & $50k Volume
        if liquidity_usd < 100000 or volume_24h < 50000: return None, None

        chain_display_name = CHAIN_MAP.get(chain_id, chain_id.upper())

        # Social Links dari Dexscreener
        socials = target_pair.get('info', {}).get('socials', [])
        websites = target_pair.get('info', {}).get('websites', [])
        
        twitter_url, telegram_url, web_url = None, None, None
        if websites: web_url = websites[0].get('url')

        for soc in socials:
            if soc.get('type') == 'twitter': twitter_url = soc.get('url')
            if soc.get('type') == 'telegram': telegram_url = soc.get('url')

        # Skor Keselamatan Pintar (Solana Sahaja)
        risk_score = "N/A (Imbas auto di Maestro)"
        insider_status = ""
        insider_holding_pct = 0
        
        if chain_id == 'solana':
            rug_endpoint = f"https://api.rugcheck.xyz/v1/tokens/{contract_address}/report"
            rug_data = requests.get(rug_endpoint, timeout=10).json()
            risk_score = rug_data.get('score', 0)
            if risk_score >= 500: return None, None
            
            top_holders = rug_data.get('topHolders', [])
            insider_holding_pct = sum([h.get('pct', 0) for h in top_holders[:10]])
            if insider_holding_pct > 40: return None, None
            insider_status = f"\n   Insider Holding: `{insider_holding_pct:.1f}%` (Pass)"
            risk_score = f"`{risk_score}` (Safe)"

        cg_rank = cg_data.get('market_cap_rank', 'N/A')
        ath_drop = cg_data.get('ath_change_percentage', 0)
        price_24h_drop = cg_data.get('price_change_percentage_24h', 0)
        current_price = cg_data.get('current_price', 0)
        
        if liquidity_usd > 250000: lp_status = "🟢"
        else: lp_status = "🟡"

        # ==========================================
        # 💬 FORMAT TEKS LAPORAN VIP
        # ==========================================
        report = f"**Asset Identified:** {cg_data['name']} `${symbol.upper()}`\n"
        report += f"`{contract_address}`\n\n"
        
        report += f"📊 **MARKET AGGREGATE (Naratif Sektor)**\n"
        report += f"   Network        : **{chain_display_name}**\n"
        report += f"   Price          : `${current_price}`\n"
        report += f"   Global Rank    : `#{cg_rank}`\n"
        report += f"   Market Cap     : `${market_cap:,.0f}`\n"
        report += f"   Diskaun 24H    : `{price_24h_drop:.2f}%` 🩸\n"
        report += f"   Diskaun ATH    : `{ath_drop:.2f}%` 📉\n\n"
        
        report += f"⛓️ **ON-CHAIN AUDIT (Dexscreener)**\n"
        report += f"   Liquidity (LP) : `${liquidity_usd:,.0f}` {lp_status}\n"
        report += f"   24H Volume     : `${volume_24h:,.0f}` 🟢{insider_status}\n"
        report += f"   Security Score : {risk_score}\n"
        
        # ==========================================
        # 🎛️ BINA BUTANG (INLINE KEYBOARD)
        # ==========================================
        markup = InlineKeyboardMarkup()
        markup.row_width = 2 # Set kepada 2 supaya butang nampak stabil/seimbang
        
        # Butang Terminal (Tingkat 1) - Smart Routing
        if chain_id == 'solana':
            term_url = f"https://t.me/bonkbot_bot?start={contract_address}"
            btn_term = InlineKeyboardButton(f"🔫 Beli di BonkBot ({chain_display_name})", url=term_url)
        else:
            term_url = f"https://t.me/maestro?start={contract_address}"
            btn_term = InlineKeyboardButton(f"🦄 Beli di Maestro ({chain_display_name})", url=term_url)
            
        # 📰 Butang Radar Berita (X) - Carian Live Cashtag
        news_search_url = f"https://twitter.com/search?q=%24{symbol}&src=typed_query&f=live"
        btn_news = InlineKeyboardButton("📰 Radar Berita (X)", url=news_search_url)

        markup.add(btn_term)
        markup.add(btn_news)

        # Butang Sosial (Tingkat 2)
        soc_buttons = []
        if twitter_url: soc_buttons.append(InlineKeyboardButton("🐦 Twitter", url=twitter_url))
        if telegram_url: soc_buttons.append(InlineKeyboardButton("✈️ Telegram", url=telegram_url))
        if web_url: soc_buttons.append(InlineKeyboardButton("🌐 Website", url=web_url))
        if soc_buttons: markup.add(*soc_buttons)

        # Butang Analisis (Tingkat 3)
        cg_url = f"https://www.coingecko.com/en/coins/{cg_data['id']}"
        dex_url = f"https://dexscreener.com/{chain_id}/{contract_address}"
        markup.add(
            InlineKeyboardButton("🦎 CoinGecko", url=cg_url),
            InlineKeyboardButton("📊 Dexscreener", url=dex_url)
        )
        
        return report, markup
    except Exception as e:
        return None, None

def neoninja_pipeline(chat_id):
    global SYSTEM_ACTIVE, CURRENT_NARRATIVE_IDX
    print("\n[SYSTEM] Initializing V2.1 VIP OMNI-VERSE PROTOCOL...")
    
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": CG_API_KEY
    }
    
    while SYSTEM_ACTIVE:
        try:
            current_time = time.time()
            active_narrative = NARRATIVES[CURRENT_NARRATIVE_IDX]
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [📡] HUNTING SECTOR: {active_narrative.upper()}...")
            
            all_coins = []
            page = 1
            max_pages = 3 # Naik sikit ke 3 muka surat sebab kita cover banyak chain
            
            while page <= max_pages:
                if not SYSTEM_ACTIVE: break
                
                cg_url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category={active_narrative}&order=market_cap_desc&per_page=250&page={page}"
                cg_response = requests.get(cg_url, headers=headers, timeout=15)
                
                if cg_response.status_code == 200:
                    data = cg_response.json()
                    if not data: break
                    all_coins.extend(data)
                    page += 1
                    time.sleep(2.0) 
                elif cg_response.status_code == 429:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [⚠️] CG API Rate Limit Hit.")
                    break
                else: break
                    
            if all_coins:
                for coin in all_coins:
                    if not SYSTEM_ACTIVE: break
                    symbol = coin.get('symbol', '')
                    price_change_24h = coin.get('price_change_percentage_24h')
                    ath_change = coin.get('ath_change_percentage')
                    
                    if price_change_24h is not None and ath_change is not None:
                        # ⚠️ TAPISAN HARGA: Jatuh 5%-25% sehari, ATH jatuh 30%-80%
                        if -25 <= price_change_24h <= -5 and -80 <= ath_change <= -30:
                            if symbol not in MEMORY_CACHE or (current_time - MEMORY_CACHE[symbol]) > 28800: 
                                
                                report, markup = verify_on_chain(symbol, coin)
                                
                                if report and markup:
                                    MEMORY_CACHE[symbol] = current_time
                                    header_msg = f"🌟 **NARRATIVE ALERT: {active_narrative.replace('-', ' ').upper()}**\n\n"
                                    bot.send_message(chat_id, header_msg + report, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)
                                
                                time.sleep(1.5) 
            
            CURRENT_NARRATIVE_IDX = (CURRENT_NARRATIVE_IDX + 1) % len(NARRATIVES)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [⏳] Sector {active_narrative.upper()} Complete. Resting for 10 MINUTES...\n")
            time.sleep(600) 
            
        except Exception as e:
            time.sleep(30)

@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.reply_to(message, "✅ **NEONINJA ORACLE PROTOCOL**\nStatus: ON STANDBY\nType `/scan` to initiate monitoring.")

@bot.message_handler(commands=['scan'])
def engage_scanner(message):
    global SYSTEM_ACTIVE
    if SYSTEM_ACTIVE: return
    SYSTEM_ACTIVE = True
    
    intro_msg = "🟢 **NEONINJA— VIP ACTIVE**"
    
    bot.reply_to(message, intro_msg)
    threading.Thread(target=neoninja_pipeline, args=(message.chat.id,), daemon=True).start()

@bot.message_handler(commands=['stop'])
def disengage_scanner(message):
    global SYSTEM_ACTIVE
    SYSTEM_ACTIVE = False
    bot.reply_to(message, "🔴 Ninja Mode Disconnected")

if __name__ == "__main__":
    bot.polling(none_stop=True)
