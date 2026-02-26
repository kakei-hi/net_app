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
def list():
    return render_template('list.html')

# detail
@app.route('/detail')
def detail():
    return render_template('detail.html')   

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
