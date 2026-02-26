# Flask本格入門　list 3.9 url_forのサンプルコード
from flask import Flask, url_for

app = Flask(__name__)

@app.route('/')
def show_index():
    return 'indexページ'

@app.route('/hello')
@app.route('/hello/<name>')
def show_hello(name=None):
    if name:
        return f'hello {name}!'
    else:
        return 'hello world!'
    
if __name__ == '__main__':
    with app.test_request_context():
        print(url_for('show_index'))
        print(url_for('show_hello'))
        print(url_for('show_hello', name='Alice'))
