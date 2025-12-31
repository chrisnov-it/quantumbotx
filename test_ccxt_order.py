import logging
import os
from dotenv import load_dotenv
from core.factory.broker_factory import BrokerFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FirstOrder")
load_dotenv()

def test_place_live_order():
    exchange_id = os.getenv('EXCHANGE_ID', 'binance')
    logger.info(f"1. Init Broker: {exchange_id} (Testnet)")
    
    try:
        # BrokerFactory akan inisialisasi pake .env (API Key, Secret, dll)
        broker = BrokerFactory.get_broker('CCXT', exchange_id=exchange_id)
        
        if not broker or not broker.exchange:
            logger.error("❌ Gagal inisialisasi Broker. Cek .env Anda!")
            return

        symbol = 'BTC/USDT'
        logger.info(f"2. Mengirim Order: BUY {symbol}")

        # Kita coba beli jumlah kecil, misal 0.01 BTC (satuan kontrak di Futures)
        success = broker.place_order(
            symbol=symbol,
            order_type='BUY',
            volume=0.01,
            comment="Order dari QuantumBotX"
        )

        if success:
            logger.info("✅ BERHASIL! Order telah dieksekusi di Exchange.")
            
            # Beri jeda sebentar agar data di bursa ter-update
            import time
            logger.info("Menunggu data posisi terupdate...")
            time.sleep(2)
            
            # Cek daftar posisi terbuka
            positions = broker.get_open_positions()
            print("\n" + "="*50)
            print("POSISI TERBUKA SAAT INI:")
            print("="*50)
            if not positions:
                print("Tidak ada posisi aktif (mungkin langsung tertutup atau error).")
            for pos in positions:
                side_str = "BUY (Long)" if pos['type'] == 0 else "SELL (Short)"
                print(f"- Symbol: {pos['symbol']}")
                print(f"  Type  : {side_str}")
                print(f"  Volume: {pos['volume']}")
                print(f"  Price : {pos['price']}")
                print(f"  Profit: {pos['profit']} USDT")
                print("-" * 20)
        else:
            logger.error("❌ Gagal menempatkan order. Cek log error di atas.")
            
    except Exception as e:
        logger.error(f"❌ Terjadi kesalahan fatal: {e}", exc_info=True)

if __name__ == "__main__":
    test_place_live_order()
