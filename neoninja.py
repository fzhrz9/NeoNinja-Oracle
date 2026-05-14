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
    return "STATUS: OK | NEONINJA SWING ORACLE (V1.4 VIP API) OPERATIONAL"

def initialize_daemon():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

daemon_thread = threading.Thread(target=initialize_daemon, daemon=True)
daemon_thread.start()

# ==========================================
# 📡 TELEGRAM & COINGECKO API KEYS
# ==========================================
API_TOKEN = '8673710597:AAGD4I53588YSL1QK9ZllzlaeQY68gFttSQ' 
CG_API_KEY = 'CG-b4VSbfrpCgK5seMpcHssGJe7' # Kunci VIP Pasport CoinGecko

bot = telebot.TeleBot(API_TOKEN)

MEMORY_CACHE = {} 
SYSTEM_ACTIVE = False 

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
        
        # ⚠️ SYARAT DILONGGARKAN: Minimum $30k LP (Sesuai untuk Swing Mid-Cap)
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
        
        report = f"🥷 **NEONINJA SWING SIGNAL (VIP)** 🥷\n"
        report += f"*(Verified by CoinGecko & On-Chain)*\n\n"
        report += f"Asset: **{cg_data['name']} (${cg_data['symbol'].upper()})**\n"
        report += f"`{contract_address}`\n\n"
        
        report += f"📊 **CoinGecko Status (Sah)**\n"
        report += f"Global Rank : **#{cg_rank}**\n"
        report += f"Market Cap : **${cg_data.get('market_cap', 0):,.0f}**\n"
        report += f"Diskaun 24H : **{price_24h_drop:.2f}%** 🩸\n"
        report += f"Diskaun ATH : **{ath_drop:.2f}%** 📉\n\n"
        
        report += f"⛓️ **On-Chain Health (Dexscreener)**\n"
        report += f"Liquidity (LP) : **${liquidity_usd:,.0f}** 🟢\n"
        report += f"Top 10 Wallets : **{insider_holding_pct:.1f}%**\n"
        report += f"RugCheck Score : **{risk_score}** (Safe)\n\n"
        
        report += f"🔗 **Intel & Execution**\n"
        report += f"🔫 [Terminal (BonkBot)](https://t.me/bonkbot_bot?start={contract_address})\n"
        report += f"🦎 [CoinGecko Page](https://www.coingecko.com/en/coins/{cg_data['id']})\n"
        report += f"📊 [Dexscreener](https://dexscreener.com/solana/{contract_address})"
        
        return report
    except Exception as e:
        return None

def neoninja_pipeline(chat_id):
    global SYSTEM_ACTIVE
    print("\n[NEONINJA] Mengaktifkan Otak Hibrid (V1.4 VIP API)...")
    
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": CG_API_KEY
    }
    
    while SYSTEM_ACTIVE:
        try:
            current_time = time.time()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🦎 Menyedut pangkalan data CoinGecko (Laluan VIP)...")
            
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
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 📥 Muka surat {page} disedut. ({len(all_coins)} koin dikumpul...)")
                    page += 1
                    time.sleep(2.0) # Boleh lajukan sikit sebab dah ada VIP Key
                elif cg_response.status_code == 429:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Kunci VIP pun limit bos! Rehat kejap.")
                    break
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Ralat CoinGecko HTTP {cg_response.status_code}. Skip page.")
                    break
                    
            if all_coins:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🥷 {len(all_coins)} Koin dikesan! Mula tapis Swing Setups...")
                
                for coin in all_coins:
                    if not SYSTEM_ACTIVE: break
                    
                    symbol = coin.get('symbol', '')
                    price_change_24h = coin.get('price_change_percentage_24h')
                    ath_change = coin.get('ath_change_percentage')
                    
                    # ⚠️ SYARAT DILONGGARKAN: Jatuh 5%-60% sehari, Jatuh >30% ATH
                    if price_change_24h is not None and ath_change is not None:
                        if -60 <= price_change_24h <= -5 and ath_change <= -30:
                            if symbol not in MEMORY_CACHE or (current_time - MEMORY_CACHE[symbol]) > 28800: 
                                
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Potensi dikesan: {symbol.upper()}. Mengesahkan On-Chain...")
                                report = verify_on_chain(symbol, coin)
                                
                                if report:
                                    MEMORY_CACHE[symbol] = current_time
                                    bot.send_message(chat_id, report, parse_mode='Markdown', disable_web_page_preview=True)
                                
                                time.sleep(1.5) 
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏳ Misi selesai. NeoNinja rehat 5 minit...\n")
            time.sleep(300) 
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Ralat Rangkaian. Cuba lagi dalam 30s...")
            time.sleep(30)

@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.reply_to(message, "🥷 **NEONINJA BERSEDIA.**\nTaip /scan untuk mula memburu.")

@bot.message_handler(commands=['scan'])
def engage_scanner(message):
    global SYSTEM_ACTIVE
    if SYSTEM_ACTIVE: return
    SYSTEM_ACTIVE = True
    bot.reply_to(message, "🥷 **NEONINJA DIHANTAR KE MEDAN (MOD VIP LALUAN PANTAS).**\n\n🎯 Target: Keseluruhan Solana (CoinGecko VIP)\n📉 Strategi: Swing Trade (Diskaun >5% harian & >30% ATH)\n\n*Menyelinap masuk ke pintu hadapan...*")
    threading.Thread(target=neoninja_pipeline, args=(message.chat.id,), daemon=True).start()

@bot.message_handler(commands=['stop'])
def disengage_scanner(message):
    global SYSTEM_ACTIVE
    SYSTEM_ACTIVE = False
    bot.reply_to(message, "🔴 **NEONINJA DIPANGGIL PULANG.**")

if __name__ == "__main__":
    bot.polling(none_stop=True)
