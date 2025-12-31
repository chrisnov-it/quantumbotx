import logging
import os
from dotenv import load_dotenv
from core.factory.broker_factory import BrokerFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestCCXT")
load_dotenv()

def test_ccxt_minimal():
    # 1. Pastikan env terisi
    exchange = os.getenv('EXCHANGE_ID', 'binance')
    logger.info(f"Targeting Exchange: {exchange}")

    # 2. Ambil dari Factory (Factory akan otomatis inisialisasi pake .env)
    try:
        broker = BrokerFactory.get_broker('CCXT', exchange_id=exchange)
        if broker and broker.exchange:
            logger.info(f"✅ Instance {broker.__class__.__name__} ready.")
        else:
            logger.error("❌ Failed to get initialized broker instance.")
            return
    except Exception as e:
        logger.error(f"❌ Factory Error: {e}")
        return

    # 3. Test Ambil Data (Public)
    symbol = 'BTC/USDT'
    logger.info(f"Fetching Rates for {symbol}...")
    try:
        df = broker.get_rates(symbol, 'H1', 5)
        if not df.empty:
            logger.info("✅ Profit! Data received:")
            print(df[['time', 'close', 'tick_volume']].tail())
        else:
            logger.warning("⚠️ Connected, but DataFrame is empty. Check if symbol exists.")
    except Exception as e:
        logger.error(f"❌ Request Error: {e}")

if __name__ == "__main__":
    test_ccxt_minimal()