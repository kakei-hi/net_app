from flask import Flask, render_template

# Create a Flask application instance
app = Flask(__name__)

# ========================================
# Routing settings
# ========================================
# Top page of the website
@app.route('/')
def index():
    return render_template('top.html')

# list
@app.route('/list')
def item_list():
    return render_template('list.html')

# detail
@app.route('/detail/<int:id>/<name>')
def item_detail(id, name):
    return render_template('detail.html', show_id=id, show_name=name)

# render_templateで値を渡す: 複数
@app.route('/multiple')
def show_jinja_multiple():
    word1 = 'テンプレートエンジン'
    word2 = '神社'
    return render_template('jinja/show1.html', temp=word1, jinja=word2)

# render_templateで値を渡す: 辞書
@app.route('/dict')
def show_jinja_dict():
    data = {
        'temp': 'テンプレートエンジン',
        'jinja': 'jinja',
        'language': 'Python'
    }
    return render_template('jinja/show2.html', key=data)

# render_templateで値を渡す: リスト
@app.route('/list2')
def show_jinja_list():
    user_name = ['桃太郎', '金太郎', '浦島太郎']
    return render_template('jinja/show3.html', users = user_name)

# render_templateで値を渡す: クラス
class User:
    # コンスタントラクタ
    def __init__(self, name, age):
        self.name = name
        self.age = age
    # メソッド（表示用）
    def __str__(self):
        return f"名前: {self.name}, 年齢: {self.age}"
    
@app.route('/class')
def show_jinja_class():
    user1 = User('太郎', 20)
    user2 = User('花子', 25)
    return render_template('jinja/show4.html', user1=user1, user2=user2)

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
