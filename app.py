from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Crypto Scanner is Online!'

@app.route('/api/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    app.run()
