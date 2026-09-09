from flask import Flask, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# محاولة استيراد Binance (قد لا يكون متوفراً في البيئة الأولى)
try:
    from binance.client import Client
    BINANCE_AVAILABLE = True
except:
    BINANCE_AVAILABLE = False

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'binance_available': BINANCE_AVAILABLE
    }), 200

@app.route('/api/scan', methods=['GET'])
def scan():
    if not BINANCE_AVAILABLE:
        return jsonify({
            'error': 'Binance client not available',
            'count': 0,
            'coins': []
        }), 200
    
    try:
        client = Client()
        results = []
        
        tickers = client.get_all_tickers()[:50]
        
        for ticker in tickers:
            symbol = ticker['symbol']
            if symbol.endswith('USDT'):
                results.append({
                    'symbol': symbol,
                    'price': ticker['price']
                })
        
        return jsonify({
            'count': len(results),
            'coins': results,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e),
            'count': 0
        }), 200

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'Crypto Scanner API',
        'endpoints': [
            '/api/health',
            '/api/scan',
            '/api/scan/<symbol>'
        ]
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
