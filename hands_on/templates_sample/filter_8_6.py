from flask import Flask, render_template

app = Flask(__name__)

@app.template_filter('add_san')
def add_san_filter(name):
    return name + "さん"

@app.template_filter('shout')
def shout_filter(message):
    return message.upper() + "!!!"

@app.template_filter('add_title')
def add_title(name, title): # 第1引数(name)にパイプの左側の値が入る
    return title + name.upper()

@app.route('/sample3/<string:name>')
def sample1(name):
    return render_template('filter_sample_3.html', name=name)

@app.route('/sample4/<string:message>')
def sample2(message):
    return render_template('filter_sample_4.html', message=message)

@app.route('/sample5/<string:name>/<string:title>')
def sample3(name, title):
    return render_template('filter_sample_5.html', name=name, title=title)

if __name__ == '__main__':
    app.run(debug=True)
