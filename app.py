from flask import Flask, jsonify
from binance.client import Client
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')

try:
    client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
except:
    client = None

def calculate_rsi(prices, period=14):
    deltas = pd.Series(prices).diff()
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    return rsi

def scan_coins():
    results = []
    try:
        tickers = client.get_all_tickers()
        
        for ticker in tickers[:50]:
            symbol = ticker['symbol']
            
            if not symbol.endswith('USDT'):
                continue
            
            try:
                klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=50)
                
                closes = [float(kline[4]) for kline in klines]
                volumes = [float(kline[7]) for kline in klines]
                
                rsi = calculate_rsi(closes)
                current_price = closes[-1]
                prev_price = closes[-2]
                price_change_percent = ((current_price - prev_price) / prev_price) * 100
                avg_volume = sum(volumes[-10:]) / 10
                current_volume = volumes[-1]
                
                if (rsi < 30 and price_change_percent > 1 and current_volume > avg_volume * 1.5):
                    results.append({
                        'symbol': symbol,
                        'price': current_price,
                        'rsi': round(rsi, 2),
                        'price_change': round(price_change_percent, 2),
                        'volume_ratio': round(current_volume / avg_volume, 2),
                        'timestamp': datetime.now().isoformat()
                    })
            except:
                pass
        
        return results
    except:
        return []

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/scan', methods=['GET'])
def scan():
    coins = scan_coins()
    return jsonify({
        'count': len(coins),
        'coins': coins,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/scan/<symbol>', methods=['GET'])
def scan_specific(symbol):
    try:
        symbol = symbol.upper()
        if not symbol.endswith('USDT'):
            symbol += 'USDT'
        
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=50)
        closes = [float(kline[4]) for kline in klines]
        
        rsi = calculate_rsi(closes)
        
        return jsonify({
            'symbol': symbol,
            'current_price': closes[-1],
            'rsi': round(rsi, 2),
            'status': 'oversold' if rsi < 30 else 'normal' if rsi < 70 else 'overbought'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
