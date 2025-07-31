# core/utils/external.py

import os
import requests
import MetaTrader5 as mt5
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

CMC_API_KEY = os.getenv("CMC_API_KEY")
CMC_API_BASE_URL = os.getenv("CMC_API_BASE_URL", "https://pro-api.coinmarketcap.com")
if not CMC_API_KEY:
    logger.warning("CMC_API_KEY not found in .env file.")

def get_crypto_data_from_cmc():
    url = f"{CMC_API_BASE_URL}/v1/cryptocurrency/listings/latest"
    headers = {'Accepts': 'application/json', 'X-CMC-PRO-API-KEY': CMC_API_KEY}
    params = {'start': '1', 'limit': '5', 'convert': 'IDR', 'sort': 'market_cap', 'sort_dir': 'desc'}

    logger.info(f"Fetching crypto data from CMC. API Key present: {bool(CMC_API_KEY)}")
    try:
        res = requests.get(url, headers=headers, params=params)
        res.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = res.json().get('data', [])
        logger.info(f"Received {len(data)} crypto entries from CMC.")
        crypto_list = []
        for c in data:
            quote = c.get('quote', {}).get('IDR', {})
            crypto_list.append({
                'name': c.get('name'),
                'symbol': c.get('symbol'),
                'price': f"Rp {quote.get('price', 0):,.2f}".replace(',', '.'),
                'change': f"{quote.get('percent_change_24h', 0):.2f}%",
                'market_cap': f"Rp {quote.get('market_cap', 0):,.0f}".replace(',', '.')
            })
        return crypto_list
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching crypto data from CMC: {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred fetching crypto data from CMC: {e}")
        return []

def get_mt5_symbol_profile(symbol):
    if not mt5.initialize():
        print("MT5 initialization failed in external.py")
        return None

    symbol_info = mt5.symbol_info(symbol)
    mt5.shutdown()

    if symbol_info:
        return {
            "name": symbol_info.description,
            "symbol": symbol_info.name,
            "currency_base": symbol_info.currency_base,
            "currency_profit": symbol_info.currency_profit,
            "digits": symbol_info.digits,
            "spread": symbol_info.spread,
            "trade_contract_size": symbol_info.trade_contract_size,
            "volume_min": symbol_info.volume_min,
            "volume_max": symbol_info.volume_max,
            "volume_step": symbol_info.volume_step,
            "margin_initial": symbol_info.margin_initial,
            "margin_maintenance": symbol_info.margin_maintenance,
        }
    return None
