        # ==========================================
        # 🎛️ BINA BUTANG (INLINE KEYBOARD)
        # ==========================================
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        
        # Tingkat 1: Bot Telegram
        if chain_id == 'solana':
            term_url = f"https://t.me/bonkbot_bot?start={contract_address}"
            btn_term = InlineKeyboardButton(f"🔫 Beli di BonkBot ({chain_display_name})", url=term_url)
        else:
            term_url = f"https://t.me/maestro?start={contract_address}"
            btn_term = InlineKeyboardButton(f"🦄 Beli di Maestro ({chain_display_name})", url=term_url)
        markup.add(btn_term)
            
        # Tingkat 2: Binance (CEX) & Radar Berita
        # ⚠️ KOD DIBAIKI: Buang 'www.' dan '/en/' supaya Android terus tangkap masuk App
        binance_url = f"https://binance.com/trade/{symbol.upper()}_USDT"
        btn_binance = InlineKeyboardButton("🟨 Beli di Binance", url=binance_url)
        
        news_search_url = f"https://twitter.com/search?q=%24{symbol}&src=typed_query&f=live"
        btn_news = InlineKeyboardButton("📰 Radar Berita (X)", url=news_search_url)
        
        markup.add(btn_binance, btn_news)

        # Tingkat 3: Sosial
        soc_buttons = []
        if twitter_url: soc_buttons.append(InlineKeyboardButton("🐦 Twitter", url=twitter_url))
        if telegram_url: soc_buttons.append(InlineKeyboardButton("✈️ Telegram", url=telegram_url))
        if web_url: soc_buttons.append(InlineKeyboardButton("🌐 Website", url=web_url))
        if soc_buttons: markup.add(*soc_buttons)

        # Tingkat 4: Analisis
        # ⚠️ KOD DIBAIKI: Buang 'www.' dan '/en/' untuk CoinGecko
        cg_url = f"https://coingecko.com/coins/{cg_data['id']}"
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
    print("\n[SYSTEM] Initializing V2.4 BINANCE INTEGRATION PROTOCOL...")
    
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
            max_pages = 3
            
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
                        if -35 <= price_change_24h <= -2 and -90 <= ath_change <= -30:
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
    
    intro_msg = "🟢 **NEONINJA— VIP ACTIVE (BINANCE INTEGRATED)**\n"
    intro_msg += "*— Radar 10 Sektor dibuka. Menyelam sekarang...*"
    
    bot.reply_to(message, intro_msg)
    threading.Thread(target=neoninja_pipeline, args=(message.chat.id,), daemon=True).start()

@bot.message_handler(commands=['stop'])
def disengage_scanner(message):
    global SYSTEM_ACTIVE
    SYSTEM_ACTIVE = False
    bot.reply_to(message, "🔴 Ninja Mode Disconnected")

if __name__ == "__main__":
    bot.polling(none_stop=True)
