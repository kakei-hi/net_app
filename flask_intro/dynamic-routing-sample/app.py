# Flask本格入門 list 2.9
from flask import Flask

# Flaskクラスのインスタンスを作成
app = Flask(__name__)

# =========================================
# ルーティングの設定
# =========================================
# コンバータなし
@app.route('/dynamic/<value>')
def dynamic_default(value):
    print(f'型: {type(value)}, 値: {value}')
    return f'<h1>渡された値: {value}</h1>'

# コンバータあり
@app.route('/dynamic2/<int:number>')
def dynamic_converter(number):
    print(f'型: {type(number)}, 値: {number}')
    return f'<h1>渡された値: {number}</h1>'

# コンバータ有り（複数）
@app.route('/dynamic3/<value>/<int:number>')
def dynamic_converter_multiple(value, number):
    print(f'valueの型: {type(value)}, 値: {value}')
    print(f'numberの型: {type(number)}, 値: {number}')
    return f'<h1>渡された値 value: {value}, number: {number}</h1>'

# =========================================
# アプリケーションの起動
# =========================================
if __name__ == '__main__':
    app.run(debug=True)
