import requests
import json
import logging

# Kemas kini ID kau di bahagian atas skrip:
VIP_CHANNEL_ID = "-1003943365561" 
ADMIN_ID = "970309251"            

# =====================================================================
# MODUL 2A: PAIP DATA API (COINGECKO & DEXSCREENER)
# =====================================================================
def get_coingecko_categories():
    """Tarik semua data 100+ sektor dari CoinGecko (Untuk Enjin 2)"""
    url = "https://api.coingecko.com/api/v3/coins/categories"
    headers = {"accept": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Ralat CoinGecko: {response.status_code}")
            return []
    except Exception as e:
        logging.error(f"Gagal sambung ke CoinGecko: {e}")
        return []

def get_dexscreener_data(contract_address):
    """Tarik data On-Chain terperinci dari Dexscreener (Liquidity, Vol, Price)"""
    url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "pairs" in data and len(data["pairs"]) > 0:
                # Ambil kolam kecairan (pair) yang paling besar/utama
                return data["pairs"][0]
        return None
    except Exception as e:
        logging.error(f"Gagal sambung ke Dexscreener: {e}")
        return None

# =====================================================================
# MODUL 2B: PELAKSANAAN DUAL-ENGINE
# =====================================================================
def engine_two_satellite_scan():
    """
    ENJIN 2: Dinamik. Cari Top 3 Sektor Paling Untung (Profit > 5%, Vol > $500M)
    """
    logging.info("🔥 Mengaktifkan Enjin 2 (The Satellite)...")
    categories = get_coingecko_categories()
    
    if not categories:
        logging.warning("Tiada data sektor diterima. Batal kitaran Enjin 2.")
        return

    valid_sectors = []
    
    # Jaring Penapis Keuntungan Institusi
    for cat in categories:
        try:
            # CoinGecko memulangkan market_cap_change_24h dan volume_24h
            market_cap_change = cat.get('market_cap_change_24h', 0) or 0
            volume_24h = cat.get('volume_24h', 0) or 0
            
            # Sweet Spot Enjin 2: Mesti Hijau (Profit) > 5% & Volume > $500 Juta
            if market_cap_change > 5.0 and volume_24h > 500000000:
                valid_sectors.append({
                    "name": cat['name'],
                    "id": cat['id'],
                    "profit": market_cap_change,
                    "volume": volume_24h
                })
        except Exception:
            continue

    # Susun ikut profit paling tinggi (Top Gainers)
    valid_sectors = sorted(valid_sectors, key=lambda x: x['profit'], reverse=True)
    top_3_sectors = valid_sectors[:3]

    if not top_3_sectors:
        logging.info("Tiada sektor melepasi Jaring Keuntungan hari ini.")
        return

    logging.info(f"Top 3 Sektor dikesan: {[s['name'] for s in top_3_sectors]}")
    
    # Seterusnya: Skrip akan menyedut koin-koin di dalam top_3_sectors ini
    # dan menghantarnya ke analyze_asset() untuk kiraan Fibo & Smart Money.
    # (Logik iterasi koin akan dimasukkan di bahagian analisis data).

def engine_one_core_scan():
    """
    ENJIN 1: Statik. Imbas naratif fundamental tinggi.
    """
    logging.info("⚙️ Mengaktifkan Enjin 1 (The Core)...")
    # Skrip akan menggunakan senarai CORE_NARRATIVES dan menarik senarai koin
    # dari kategori tersebut melalui CoinGecko, kemudian diserahkan ke analyze_asset().
    pass
