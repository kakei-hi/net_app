#!/usr/bin/env python3
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key")
# Use absolute path for SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
default_db_path = f"sqlite:///{os.path.join(basedir, 'database', 'app.db')}"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", default_db_path)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Ensure the database directory exists
db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
if db_uri.startswith("sqlite:///"):
    db_path = db_uri.replace("sqlite:///", "")
    # Handle absolute path if it starts with another slash
    if db_path.startswith("/"):
        db_path = "/" + db_path.lstrip("/")
    db_dir = os.path.dirname(os.path.abspath(db_path))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

@app.route("/")
def index():
    count = Message.query.count()
    return render_template("index.html", count=count)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if Message.query.count() == 0:
            db.session.add(Message(content="Hello, Flask + mamba + SQLite!"))
            db.session.commit()
    app.run(debug=True)
