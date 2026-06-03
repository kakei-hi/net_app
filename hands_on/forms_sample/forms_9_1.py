from flask import Flask, render_template, request

app = Flask(__name__)

# GETリクエストを処理するルート
@app.route('/get')
def do_get():
    name = request.args.get('name')
    return f'Hello, {name}さん!'

# POSTリクエストを処理するルート
@app.route('/', methods=['GET', 'POST'])
def do_get_post():
    if request.method == 'POST':
        name = request.form.get('name')
        return f'Hello, {name}さん!'
    return render_template('form_9_1.html')

if __name__ == '__main__':
    app.run(debug=True)

