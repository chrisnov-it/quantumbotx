# core/backtesting/engine.py

import pandas_ta as ta
from core.strategies.strategy_map import STRATEGY_MAP

def run_backtest(strategy_id, params, historical_data_df):
    """
    Menjalankan simulasi backtesting untuk strategi tertentu pada data historis.
    VERSI BARU: Menggunakan SL/TP dinamis berbasis ATR.
    """
    strategy_class = STRATEGY_MAP.get(strategy_id)
    if not strategy_class:
        return {"error": "Strategi tidak ditemukan"}

    # --- LANGKAH 1: Pra-perhitungan Indikator & ATR ---
    class MockBot:
        def __init__(self):
            self.market_for_mt5 = "BACKTEST"
            self.timeframe = "H1"
            self.tf_map = {}

    strategy_instance = strategy_class(bot_instance=MockBot(), params=params)
    df_with_signals = strategy_instance.analyze_df(historical_data_df.copy())

    # Hitung ATR untuk SL/TP dinamis
    df_with_signals.ta.atr(length=14, append=True)
    # Hapus baris dengan nilai NaN setelah perhitungan indikator
    df_with_signals.dropna(inplace=True)
    df_with_signals.reset_index(inplace=True) # Pastikan kita bisa iterasi dengan iloc

    if df_with_signals.empty:
        return {"error": "Gagal menghasilkan data indikator/ATR. Periksa panjang data input."}

    strategy_name = strategy_instance.name

    # --- LANGKAH 2: Inisialisasi state backtesting ---
    trades = []
    in_position = False
    initial_capital = 10000
    capital = initial_capital
    equity_curve = [initial_capital]
    peak_equity = initial_capital
    max_drawdown = 0.0
    
    position_type = None
    entry_price = 0.0
    entry_time = None
    sl_price = 0.0
    tp_price = 0.0

    # Ambil multiplier dari params. Nama kunci masih 'sl_pips' & 'tp_pips' untuk konsistensi dengan DB.
    # Konversi ke float untuk memastikan kalkulasi berjalan baik
    sl_atr_multiplier = float(params.get('sl_pips', 2.0))
    tp_atr_multiplier = float(params.get('tp_pips', 4.0))

    # --- LANGKAH 3: Loop melalui data ---
    for i in range(1, len(df_with_signals)):
        current_bar = df_with_signals.iloc[i]
        
        # Cek SL/TP jika sedang dalam posisi
        if in_position:
            exit_price = None
            reason = ''
            
            if position_type == 'BUY':
                # Cek SL
                if current_bar['low'] <= sl_price:
                    exit_price = sl_price
                    reason = 'SL'
                # Cek TP
                elif current_bar['high'] >= tp_price:
                    exit_price = tp_price
                    reason = 'TP'
            
            elif position_type == 'SELL':
                # Cek SL
                if current_bar['high'] >= sl_price:
                    exit_price = sl_price
                    reason = 'SL'
                # Cek TP
                elif current_bar['low'] <= tp_price:
                    exit_price = tp_price
                    reason = 'TP'

            # Proses penutupan posisi jika SL/TP tercapai
            if exit_price is not None:
                # Asumsi 1 lot standar untuk kalkulasi profit/loss
                profit = (exit_price - entry_price) if position_type == 'BUY' else (entry_price - exit_price)
                trades.append({
                    'entry_time': str(entry_time), # Lebih aman dari strftime
                    'exit_time': str(current_bar['time']), # Lebih aman dari strftime
                    'entry': entry_price, 
                    'exit': exit_price, 
                    'profit_pips': profit, 
                    'reason': reason, 
                    'position_type': position_type
                })
                capital += profit
                equity_curve.append(capital)
                peak_equity = max(peak_equity, capital)
                drawdown = (peak_equity - capital) / peak_equity if peak_equity > 0 else 0
                max_drawdown = max(max_drawdown, drawdown)
                in_position = False
                position_type = None

        # Cek sinyal baru (hanya jika tidak ada posisi)
        if not in_position:
            signal = current_bar.get("signal", "HOLD")
            if signal == 'BUY' or signal == 'SELL':
                in_position = True
                position_type = signal
                entry_price = current_bar['close']
                entry_time = current_bar['time']
                
                # Ambil ATR pada bar sinyal untuk menentukan SL/TP
                atr_value = current_bar['ATRr_14']
                if atr_value > 0:
                    sl_distance = atr_value * sl_atr_multiplier
                    tp_distance = atr_value * tp_atr_multiplier
                    
                    if signal == 'BUY':
                        sl_price = entry_price - sl_distance
                        tp_price = entry_price + tp_distance
                    else: # SELL
                        sl_price = entry_price + sl_distance
                        tp_price = entry_price - tp_distance
                else:
                    # Jika ATR 0, batalkan trade untuk menghindari SL/TP di harga entry
                    in_position = False
                    position_type = None

    # --- LANGKAH 4: Hitung hasil akhir ---
    total_profit = capital - initial_capital
    wins = len([trade for trade in trades if trade['profit_pips'] > 0])
    losses = len(trades) - wins
    win_rate = (wins / len(trades) * 100) if trades else 0

    return {
        "strategy_name": strategy_name,
        "total_trades": len(trades),
        "final_capital": round(capital, 2),
        "total_profit_pips": round(total_profit, 2),
        "win_rate_percent": round(win_rate, 2),
        "wins": wins,
        "losses": losses,
        "max_drawdown_percent": round(max_drawdown * 100, 2),
        "equity_curve": equity_curve,
        "trades": trades[-20:] # Hanya tampilkan 20 trade terakhir
    }
