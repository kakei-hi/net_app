from flask import Flask, render_template

app = Flask(__name__)

@app.route('/sample1/<string:name>')
def sample1(name):
    return render_template('filter_sample_1.html', name=name)

@app.route('/sample2/<string:name>/<string:message>')
def sample2(name, message):
    return render_template('filter_sample_2.html', name=name, message=message)

if __name__ == '__main__':
    app.run(debug=True)
