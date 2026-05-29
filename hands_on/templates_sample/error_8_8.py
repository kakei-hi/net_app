from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return "トップページ"

@app.route('/test-error')
def test_error():
    # 意図的に500エラーを発生させる
    raise Exception("テスト用エラー")

# 404エラー処理
@app.errorhandler(404)
def page_not_found(error):
    return render_template('error_404.html'), 404

# 500エラー処理
@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error_500.html'), 500

if __name__ == '__main__':
#    app.run(debug=True)
    app.run(debug=False)
