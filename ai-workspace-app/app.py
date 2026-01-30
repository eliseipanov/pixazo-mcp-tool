# app.py
from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-me'  # placeholder

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    app.run(debug=True)