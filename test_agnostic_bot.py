
import logging
import pandas as pd
from core.bots.trading_bot import TradingBot
from core.interfaces.broker_interface import BrokerInterface

# Configure logging
logging.basicConfig(level=logging.INFO)

class MockBroker(BrokerInterface):
    def __init__(self):
        self.positions = []
        self._ticket_counter = 1000

    def initialize(self, credentials): 
        return True
    
    def get_account_info(self): 
        return {'balance': 10000, 'equity': 10000}
    
    def get_rates(self, symbol, timeframe, count=100):
        # Mengembalikan DataFrame dengan format yang tepat
        # Dibuat lebih banyak baris (count) untuk simulasi indikator strategi
        data = {
            'time': pd.date_range(end=pd.Timestamp.now(), periods=count, freq='H'),
            'open': [1.0] * count,
            'high': [1.1] * count,
            'low': [0.9] * count,
            'close': [1.05] * count,
            'tick_volume': [100] * count
        }
        return pd.DataFrame(data)
    
    def get_open_positions(self): 
        return self.positions
    
    def place_order(self, symbol: str, order_type: str, volume: float, price: float = 0.0, sl: float = 0.0, tp: float = 0.0, comment: str = ""): 
        self._ticket_counter += 1
        # Ekstrak magic number dari comment (Bot-ID) agar bot bisa mengenali posisinya
        magic = int(comment.split('-')[1]) if 'Bot-' in comment else 0
        
        new_pos = {
            'ticket': self._ticket_counter,
            'symbol': symbol,
            'type': order_type,
            'volume': volume,
            'price': price,
            'sl': sl,
            'tp': tp,
            'magic': magic,
            'profit': 10.5 # Dummy profit
        }
        self.positions.append(new_pos)
        print(f"MOCK ORDER PLACED: {new_pos}")
        return True
    
    def close_position(self, position_id, volume: float = 0.0): 
        # Menghapus posisi dari list internal berdasarkan ticket
        self.positions = [p for p in self.positions if str(p['ticket']) != str(position_id)]
        print(f"MOCK POSITION CLOSED: ID {position_id}")
        return True
    
    def get_symbol_info(self, symbol): 
        return {'name': symbol, 'digits': 5}
    
    def get_todays_profit(self): 
        return 50.0

def test_bot_initialization():
    print("Testing Bot initialization with Mock Broker...")
    mock_broker = MockBroker()
    bot = TradingBot(
        id=999,
        name="MockBot",
        market="EURUSD",
        risk_percent=1.0,
        sl_pips=50,
        tp_pips=100,
        timeframe="H1",
        check_interval=1,
        strategy="MA_CROSSOVER", # Real strategy from STRATEGY_MAP
        broker=mock_broker
    )
    
    # We won't actually start the thread in this test to avoid loop
    print(f"Bot '{bot.name}' initialized successfully with broker {bot.broker.__class__.__name__}")
    assert bot.broker == mock_broker
    print("Initialization Test passed!")

def test_full_trade_loop():
    print("\n--- Testing Full Trade Loop (Simulation) ---")
    mock_broker = MockBroker()
    
    # Setup bot
    bot = TradingBot(
        id=777,
        name="LoopTester",
        market="EURUSD",
        risk_percent=0.1,
        sl_pips=50,
        tp_pips=100,
        timeframe="H1",
        check_interval=0.1,
        strategy="MA_CROSSOVER", 
        broker=mock_broker
    )
    
    # Pre-setup manually for testing internal logic
    bot.market_for_mt5 = "EURUSD"
    from core.strategies.strategy_map import STRATEGY_MAP
    bot.strategy_instance = STRATEGY_MAP["MA_CROSSOVER"](bot_instance=bot)

    # 1. Simulasikan Sinyal BUY
    print("\n[Step 1] Simulating BUY Signal...")
    # Bot handle signal (no position yet)
    bot._handle_trade_signal('BUY', None)
    
    positions = mock_broker.get_open_positions()
    assert len(positions) == 1
    assert positions[0]['type'] == 'BUY'
    print(f"Verified: Position opened successfully. Ticket: {positions[0]['ticket']}")

    # 2. Simulasikan Sinyal SELL (Bot harus tutup BUY dulu baru buka SELL)
    print("\n[Step 2] Simulating SELL Signal while BUY is open...")
    # Get current position like the bot loop does
    current_pos = bot._get_open_position()
    assert current_pos is not None
    
    # Trigger signal handler
    bot._handle_trade_signal('SELL', current_pos)
    
    # Verify positions after switch
    positions = mock_broker.get_open_positions()
    assert len(positions) == 1
    assert positions[0]['type'] == 'SELL'
    print("Verification: Old BUY position was closed and new SELL position was opened!")

    print("\nFull Trade Loop Test Passed!")

if __name__ == "__main__":
    test_bot_initialization()
    test_full_trade_loop()
