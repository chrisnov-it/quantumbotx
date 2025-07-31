from flask import Blueprint, jsonify

# Initialize blueprint
api_crypto = Blueprint('api_crypto', __name__)

# Sample data for initial load
SAMPLE_CRYPTO_DATA = [
    {
        'name': 'Bitcoin',
        'symbol': 'BTC',
        'price': 'Rp 1.234,567,890.00',
        'change': '+2.34%',
        'market_cap': 'Rp 2.345,678,901,234.00'
    },
    {
        'name': 'Ethereum',
        'symbol': 'ETH',
        'price': 'Rp 123,456,789.00',
        'change': '-1.23%',
        'market_cap': 'Rp 1.234,567,890,123.00'
    }
]

@api_crypto.route('/api/crypto')
def get_crypto_data():
    """Get cryptocurrency market data"""
    try:
        # Try to get real data from CMC
        from core.utils.external import get_crypto_data_from_cmc
        real_data = get_crypto_data_from_cmc()
        
        if real_data and len(real_data) > 0:
            return jsonify(real_data)
            
        # Fallback to sample data if API fails
        return jsonify(SAMPLE_CRYPTO_DATA)
    except Exception as e:
        # Return error response
        return jsonify({'error': str(e)}), 500
