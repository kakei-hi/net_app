from flask import Flask, render_template

app = Flask(__name__)

@app.route('/sample1/<int:age>')
def sample1(age):
    return render_template('template_sample_1.html', age=age)

@app.route('/sample2')
def sample2():
    items = ['りんご', '', 'バナナ', '', 'みかん']
    return render_template('template_sample_2.html', items=items)

@app.route('/sample3')
def sample3():
    items = ['りんご', '', 'バナナ', '', 'みかん']
    return render_template('template_sample_3.html', items=items)

if __name__ == '__main__':
    app.run(debug=True)
