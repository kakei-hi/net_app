from flask import Flask

app = Flask(__name__)

#===============================
# ルーティング
#===============================
@app.route('/')
def index():
    return "Hello, Flask!"

# 動的ルーティング: コンバータなし
@app.route('/dynamic/<value>')
def dynamic(value):
    return f"Hello, {value}!"

# 動的ルーティング: コンバータあり
@app.route('/dynamic_int/<int:value>')
def dynamic_int(value):
    return f"渡された値は{value}です"

# 動的ルーティング: コンバータあり（複数）
@app.route('/dynamic_multi/<string:name>/<int:age>')
def dynamic_multi(name, age):
    return f"名前: {name}, 年齢: {age}"

#===============================
# アプリケーションの起動
#===============================
if __name__ == '__main__':
    app.run(debug=True)
