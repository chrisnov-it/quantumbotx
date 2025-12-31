import logging
import time
import pandas as pd
import random
from core.bots.trading_bot import TradingBot
from core.interfaces.broker_interface import BrokerInterface
from core.strategies.strategy_map import STRATEGY_MAP

# 1. Setup Logging yang Cantik
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-7s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("QuantumSim")

# 2. MockBroker yang Lebih Hebat (Bisa update harga)
class AdvancedMockBroker(BrokerInterface):
    def __init__(self):
        self.positions = []
        self._ticket_counter = 5000
        self.current_price = 88000.0
        self.history = []
        # Generate some initial history
        for i in range(100):
            self.current_price += random.uniform(-100, 100)
            self.history.append(self.current_price)

    def initialize(self, credentials): return True
    def get_account_info(self): return {'balance': 100000, 'equity': 100000}
    
    def get_rates(self, symbol, timeframe, count=100):
        # Update harga sedikit setiap kali dipanggil agar simulasi terasa hidup
        self.current_price += random.uniform(-150, 150)
        self.history.append(self.current_price)
        last_prices = self.history[-count:]
        
        df = pd.DataFrame({
            'time': pd.date_range(end=pd.Timestamp.now(), periods=len(last_prices), freq='H'),
            'open': [p * 0.999 for p in last_prices],
            'high': [p * 1.002 for p in last_prices],
            'low': [p * 0.998 for p in last_prices],
            'close': last_prices,
            'tick_volume': [random.randint(1000, 5000) for _ in last_prices]
        })
        return df

    def get_open_positions(self): return self.positions
    
    def place_order(self, symbol, order_type, volume, price=0.0, sl=0.0, tp=0.0, comment=""):
        self._ticket_counter += 1
        magic = int(comment.split('-')[1]) if 'Bot-' in comment else 0
        new_pos = {
            'ticket': self._ticket_counter,
            'symbol': symbol,
            'type': order_type,
            'volume': volume,
            'price': self.current_price,
            'sl': sl, 'tp': tp, 'magic': magic,
            'profit': 0.0
        }
        self.positions.append(new_pos)
        logger.info(f"✨ [BROKER] ORDER BERHASIL: {order_type} {symbol} @ {self.current_price:.2f}")
        return True

    def close_position(self, position_id, volume=0.0):
        self.positions = [p for p in self.positions if str(p['ticket']) != str(position_id)]
        logger.info(f"🛑 [BROKER] POSISI DITUTUP: ID {position_id}")
        return True

    def get_symbol_info(self, symbol): return {'name': symbol, 'digits': 2}
    def get_todays_profit(self): return 120.50

# 3. Script Simulasi Utama
def run_visual_simulation():
    print("\n" + "="*60)
    print("      QUANTUM BOT X - LIVE SIMULATION MODE (MOCK)      ")
    print("="*60)
    
    broker = AdvancedMockBroker()
    
    bot = TradingBot(
        id=1337,
        name="UltraBot-Sim",
        market="BTC/USDT",
        risk_percent=0.05,
        sl_pips=1000,
        tp_pips=2000,
        timeframe="H1",
        check_interval=2, # Cek setiap 2 detik
        strategy="MA_CROSSOVER", # Pake strategi asli
        broker=broker
    )

    # Kita jalankan loop bot secara manual agar bisa kita batasi jumlah iterasinya
    # (Biasanya bot.start() akan jalan selamanya di thread terpisah)
    
    # Setup Strategy Instance (biasanya dilakukan di bot.run())
    bot.market_for_mt5 = "BTC/USDT"
    bot.strategy_instance = STRATEGY_MAP["MA_CROSSOVER"](bot_instance=bot)
    
    print(f"Bot '{bot.name}' Ready. Menggunakan Strategi: {bot.strategy_name}")
    print("Memulai simulasi 10 iterasi...\n")

    for i in range(1, 11):
        print(f"\n--- Iterasi {i}/10 | Harga Saat Ini: {broker.current_price:.2f} ---")
        
        # Ambil data kandel
        df = broker.get_rates(bot.market_for_mt5, bot.timeframe, 50)
        
        # Analisis Strategi
        bot.last_analysis = bot.strategy_instance.analyze(df)
        
        # PAKSA SINYAL untuk demo agar terlihat log-nya
        if i == 2: signal = 'BUY'
        elif i == 5: signal = 'SELL'
        elif i == 8: signal = 'BUY'
        else: signal = bot.last_analysis.get('signal', 'HOLD')
        
        logger.info(f"Analisis: {signal} | Penjelasan: {bot.last_analysis.get('explanation', 'Manual Override for Demo' if i in [2,5,8] else '')}")
        
        # Eksekusi (Logika di TradingBot._handle_trade_signal)
        posisi_sekarang = bot._get_open_position()
        bot._handle_trade_signal(signal, posisi_sekarang)
        
        # Kasih jeda biar enak dilihat
        time.sleep(1.5)

    print("\n" + "="*60)
    print("               SIMULASI SELESAI!               ")
    print("="*60)
    print("Bot berhasil mensimulasikan logika trading tanpa menyentuh dana asli.")

if __name__ == "__main__":
    run_visual_simulation()
