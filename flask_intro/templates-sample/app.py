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

# ========================================
# テンプレートで制御文を使う
# ========================================
#  繰り返し
class Item:
    # コンストラクタ
    def __init__(self, id, name):
        self.id = id
        self.name = name
    # メソッド（表示用）
    def __str__(self):
        return f"商品ID: {self.id}, 商品名: {self.name}"

@app.route('/for_list')
def show_for_list():
    item_list = [Item(1, 'だんご'), Item(2, 'おにぎり'), Item(3, 'すし')]
    return render_template('for_list.html', items=item_list)

# 条件分岐 #1
@app.route('/if_detail/<int:id>')
def show_if_detail(id):
    item_list = [Item(1, 'だんご'), Item(2, 'おにぎり'), Item(3, 'すし')]
    return render_template('if_detail.html',show_id=id, items=item_list)

# 条件分岐 #2
@app.route('/if')
@app.route('/if/<target>')
def show_jinja_if(target='colorless'):
    print(target)
    return render_template('jinja/if_else.html', color=target)

# ========================================
# テンプレートでフィルタを使う
# ========================================
# フィルタ: 全体
@app.route('/filter')
def show_filter_block():
    word = 'pen'
    return render_template('filter/block.html', word=word)

# フィルタ: 特定の変数
@app.route('/filter2')
def show_filter_variable():
    # クラスを作成
    momo = User('桃太郎', 18)
    kinta = User('金太郎', 20)
    ura = User('浦島太郎', 100)
    kaguya = User('かぐや姫', 1000)
    kasa = User('笠地蔵', 200)
    # リストを作成
    users_list = [momo, kinta, ura, kaguya, kasa]
    return render_template('filter/filter_list.html', users=users_list)

# フィルタ: カスタムフィルタ
## カスタムフィルタを定義
@app.template_filter('truncate')
def str_truncate(value, length=10):
    if len(value) > length:
        return value[:length] + '...'
    else:
        return value
    
## カスタムフィルタを使用するルート
@app.route('/custom_filter')
def show_custom_filter():
    text = '寿限無'
    long_text = 'じゅげむじゅげむごこうのすりきれ'
    return render_template('filter/custom_filter.html', text=text, long_text=long_text)

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
