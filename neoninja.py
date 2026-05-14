import telebot
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
    return "STATUS: OK | NEONINJA ORACLE PROTOCOL (V1.5 PRO) OPERATIONAL"

def initialize_daemon():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

daemon_thread = threading.Thread(target=initialize_daemon, daemon=True)
daemon_thread.start()

# ==========================================
# 📡 TELEGRAM & COINGECKO API KEYS
# ==========================================
# ⚠️ Ganti token Telegram kau kat sini (yang baru kau dapat dari BotFather).
API_TOKEN = '8673710597:AAGD4I53588YSL1QK9ZllzlaeQY68gFttSQ' 
CG_API_KEY = 'CG-b4VSbfrpCgK5seMpcHssGJe7' # Kunci VIP Pasport CoinGecko

bot = telebot.TeleBot(API_TOKEN)

MEMORY_CACHE = {} 
SYSTEM_ACTIVE = False 

# Pembahagi garisan untuk nampak kemas
REPORT_SEPARATOR = "—" * 38

# ==========================================
# 🧠 ALGORITHM: HYBRID COINGECKO + DEXSCREENER
# ==========================================
def verify_on_chain(symbol, cg_data):
    try:
        dex_search = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={symbol}", timeout=10).json()
        if not dex_search.get('pairs'): return None
        
        target_pair = None
        for pair in dex_search['pairs']:
            if pair.get('chainId') == 'solana' and pair['baseToken']['symbol'].lower() == symbol.lower():
                target_pair = pair
                break
                
        if not target_pair: return None
        
        contract_address = target_pair['baseToken']['address']
        liquidity_usd = target_pair.get('liquidity', {}).get('usd', 0)
        
        if liquidity_usd < 30000: return None

        rug_endpoint = f"https://api.rugcheck.xyz/v1/tokens/{contract_address}/report"
        rug_data = requests.get(rug_endpoint, timeout=10).json()
        
        risk_score = rug_data.get('score', 0)
        if risk_score >= 500: return None 
        
        top_holders = rug_data.get('topHolders', [])
        insider_holding_pct = sum([h.get('pct', 0) for h in top_holders[:10]])
        if insider_holding_pct > 40: return None 

        cg_rank = cg_data.get('market_cap_rank', 'N/A')
        ath_drop = cg_data.get('ath_change_percentage', 0)
        price_24h_drop = cg_data.get('price_change_percentage_24h', 0)
        
        # 💎 FORMULASI LAPORAN VIP (NEW LOOK & COSMETICS)
        report = f"✅ **NEONINJA ORACLE | QUANTITATIVE SIGNAL** ✅\n"
        report += f"*(Multi-Source Data Verification Protocol)*\n\n"
        report += f"{REPORT_SEPARATOR}\n"
        report += f"Asset Identified:\n"
        report += f"🔹 **{cg_data['name']}** `${symbol.upper()}`\n"
        report += f"`{contract_address}`\n"
        report += f"{REPORT_SEPARATOR}\n\n"
        
        report += f"📡 **MARKET AGGREGATE DATA (CoinGecko Verified)**\n"
        report += f"   Global Position: `#{cg_rank}`\n"
        report += f"   Market Cap     : `${cg_data.get('market_cap', 0):,.0f}`\n"
        report += f"   Diskaun 24H    : `{price_24h_drop:.2f}%` 🩸\n"
        report += f"   Diskaun ATH    : `{ath_drop:.2f}%` 📉\n\n"
        
        report += f"⛓️ **ON-CHAIN AUDIT (Dexscreener Verified)**\n"
        report += f"   Real Liquidity : `${liquidity_usd:,.0f}` 🟢\n"
        report += f"   Insider Holding: `{insider_holding_pct:.1f}%` (Pass)\n"
        report += f"   Security Score : `{risk_score}` (Safe)\n\n"
        
        report += f"{REPORT_SEPARATOR}\n"
        report += f"Execution & Terminal:\n"
        report += f"🔹 [Trade terminal (BonkBot)](https://t.me/bonkbot_bot?start={contract_address})\n"
        report += f"🔹 [View On CoinGecko](https://www.coingecko.com/en/coins/{cg_data['id']})\n"
        report += f"🔹 [View On Dexscreener](https://dexscreener.com/solana/{contract_address})"
        
        return report
    except Exception as e:
        return None

def neoninja_pipeline(chat_id):
    global SYSTEM_ACTIVE
    print("\n[SYSTEM] Initializing NeoNinja Oracle Protocol (V1.5 PRO Edition)...")
    
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": CG_API_KEY
    }
    
    while SYSTEM_ACTIVE:
        try:
            current_time = time.time()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [📡] Initializing API Pull (CG VIP Portal)...")
            
            all_coins = []
            page = 1
            max_pages = 15 
            
            while page <= max_pages:
                if not SYSTEM_ACTIVE: break
                
                cg_url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=solana-ecosystem&order=market_cap_desc&per_page=250&page={page}"
                cg_response = requests.get(cg_url, headers=headers, timeout=15)
                
                if cg_response.status_code == 200:
                    data = cg_response.json()
                    if not data: 
                        break
                    
                    all_coins.extend(data)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [📥] Page {page} retrieved. ({len(all_coins)} items)")
                    page += 1
                    time.sleep(2.0) 
                elif cg_response.status_code == 429:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [⚠️] CG API Rate Limit Hit (VIP Protocol Backoff Engaged).")
                    break
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [❌] CG API Error {cg_response.status_code}. Skipping Page.")
                    break
                    
            if all_coins:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [⚙️] {len(all_coins)} Items Retrieved. Starting Multi-Source Verification...")
                
                for coin in all_coins:
                    if not SYSTEM_ACTIVE: break
                    
                    symbol = coin.get('symbol', '')
                    price_change_24h = coin.get('price_change_percentage_24h')
                    ath_change = coin.get('ath_change_percentage')
                    
                    if price_change_24h is not None and ath_change is not None:
                        if -60 <= price_change_24h <= -5 and ath_change <= -30:
                            if symbol not in MEMORY_CACHE or (current_time - MEMORY_CACHE[symbol]) > 28800: 
                                
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] [💎] Target identified: {symbol.upper()}. Verification Protocol initiated...")
                                report = verify_on_chain(symbol, coin)
                                
                                if report:
                                    MEMORY_CACHE[symbol] = current_time
                                    bot.send_message(chat_id, report, parse_mode='Markdown', disable_web_page_preview=True)
                                
                                time.sleep(1.5) 
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [⏳] Verification Cycle Complete. Protocol entered backoff phase (5 min)...\n")
            time.sleep(300) 
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [❌] Network or System Error. Resetting in 30s...")
            time.sleep(30)

@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.reply_to(message, "✅ **NEONINJA ORACLE PROTOCOL | STATUS: ON STANDBY**\nTaip `/scan` untuk memulakan pemantauan kuantitatif Solana.")

@bot.message_handler(commands=['scan'])
def engage_scanner(message):
    global SYSTEM_ACTIVE
    if SYSTEM_ACTIVE: return
    SYSTEM_ACTIVE = True
    bot.reply_to(message, "🟢 **[NEONINJA PROTOCOL] — PROTOKOL DIAKTIFKAN**\n\nSistem pemantauan data kuantitatif Solana dihidupkan.\nKunci VIP CoinGecko disahkan.\n\n*— Analisis algoritma bermula.*")
    threading.Thread(target=neoninja_pipeline, args=(message.chat.id,), daemon=True).start()

@bot.message_handler(commands=['stop'])
def disengage_scanner(message):
    global SYSTEM_ACTIVE
    SYSTEM_ACTIVE = False
    bot.reply_to(message, "🔴 **[NEONINJA PROTOCOL] — TERMINATED**\n\nOperasi pengesanan pasaran dihentikan. Semua proses pemantauan quantitative cease.")

if __name__ == "__main__":
    bot.polling(none_stop=True)
