# core/routes/api_forex.py

from flask import Blueprint, jsonify
from core.utils.symbols import get_forex_symbols
from core.utils.external import get_mt5_symbol_profile

api_forex = Blueprint('api_forex', __name__)

@api_forex.route('/api/forex-data')
def get_forex_data():
    """
    Mengembalikan daftar simbol forex, diurutkan berdasarkan popularitas (volume harian).
    Formatnya adalah array JSON, bukan dictionary, agar urutan tetap terjaga.
    """
    forex_symbols = get_forex_symbols()
    return jsonify(forex_symbols)

@api_forex.route('/api/forex/<symbol>/profile')
def get_forex_profile(symbol):
    profile = get_mt5_symbol_profile(symbol)
    if profile:
        return jsonify(profile)
    return jsonify({"error": "Could not fetch symbol profile from MT5"}), 404
