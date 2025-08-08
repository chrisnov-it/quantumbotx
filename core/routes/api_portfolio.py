# core/routes/api_portfolio.py

from flask import Blueprint, jsonify
from core.utils.mt5 import get_open_positions_mt5

# Blueprint didefinisikan dengan url_prefix untuk konsistensi
api_portfolio = Blueprint('api_portfolio', __name__, url_prefix='/api/portfolio')

@api_portfolio.route('/open-positions')
def api_open_positions():
    """Endpoint untuk menyediakan daftar posisi terbuka secara real-time."""
    try:
        positions = get_open_positions_mt5()
        return jsonify(positions)
    except Exception as e:
        # Mengembalikan error 500 jika ada masalah di backend
        return jsonify({"error": str(e)}), 500

@api_portfolio.route('/allocation')
def get_asset_allocation():
    """Endpoint untuk menghitung dan mengembalikan alokasi aset."""
    try:
        positions = get_open_positions_mt5()
        
        # Logika untuk mengklasifikasikan aset berdasarkan simbol
        allocation_summary = {
            "Forex": 0.0, "Emas": 0.0, "Saham": 0.0,
            "Crypto": 0.0, "Lainnya": 0.0
        }
        
        if positions:
            for pos in positions:
                symbol = pos.get('symbol', '').upper()
                volume = pos.get('volume', 0.0)

                if 'USD' in symbol and 'XAU' not in symbol and 'BTC' not in symbol:
                    allocation_summary["Forex"] += volume
                elif 'XAU' in symbol:
                    allocation_summary["Emas"] += volume
                elif any(stock in symbol for stock in ['AAPL', 'GOOGL', 'TSLA', 'ND100', 'SP500']):
                    allocation_summary["Saham"] += volume
                elif 'BTC' in symbol or 'ETH' in symbol:
                    allocation_summary["Crypto"] += volume
                else:
                    allocation_summary["Lainnya"] += volume
        
        # Hapus kategori dengan nilai nol untuk chart yang lebih bersih
        final_allocation = {k: v for k, v in allocation_summary.items() if v > 0}

        data = {
            "labels": list(final_allocation.keys()) or ["Belum Ada Posisi"],
            "values": list(final_allocation.values()) or [1]
        }
        return jsonify(data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
