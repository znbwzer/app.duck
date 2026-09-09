from flask import Flask, jsonify
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'Crypto Scanner API is running! 🚀',
        'status': 'online'
    }), 200

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'crypto-scanner'
    }), 200

@app.route('/api/scan', methods=['GET'])
def scan():
    return jsonify({
        'message': 'Scan endpoint - coming soon',
        'coins_found': 0,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
