from flask import Flask, render_template

app = Flask(__name__)

@app.template_filter('add_san')
def add_san_filter(nom):
    return nom + "さん"

@app.template_filter('shout')
def shout_filter(message):
    return message.upper() + "!!!"

@app.route('/sample1/<string:name>')
def sample1(name):
    return render_template('filter_sample_3.html', name=name)

@app.route('/sample2/<string:message>')
def sample2(message):
    return render_template('filter_sample_4.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
