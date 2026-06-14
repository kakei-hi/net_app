import os

from flask import Flask, flash, redirect, render_template, url_for
from flask_wtf import FlaskForm, CSRFProtect
from flask_wtf.csrf import CSRFError
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
# Flask-WTF がセッションと CSRF トークン署名に利用するキー
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-only")

# アプリ全体の POST/PUT/PATCH/DELETE に CSRF 保護を適用
csrf = CSRFProtect(app)


class ContactForm(FlaskForm):
    name = StringField("名前", validators=[DataRequired()])
    message = StringField("メッセージ", validators=[DataRequired()])
    submit = SubmitField("送信")


@app.route("/", methods=["GET", "POST"])
def index():
    form = ContactForm()

    if form.validate_on_submit():
        flash(
            f"送信成功: name={form.name.data}, message={form.message.data}",
            "ok",
        )
        return redirect(url_for("index"))

    return render_template("csrf_10_3_form.html", form=form)


@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    return render_template("csrf_10_3_error.html", reason=error.description), 400


if __name__ == "__main__":
    app.run(debug=True)
