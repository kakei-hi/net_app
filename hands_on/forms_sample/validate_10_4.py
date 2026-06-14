import os

from flask import Flask, flash, redirect, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-only")


class ContactForm(FlaskForm):
    name = StringField("名前", validators=[DataRequired(), Length(min=2, max=20)])
    message = StringField("メッセージ", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("送信")

    def validate_name(self, field):
        if field.data.lower() == "admin":
            raise ValidationError("名前に admin は使えません。")


@app.route("/", methods=["GET", "POST"])
def index():
    form = ContactForm()

    if form.validate_on_submit():
        flash(
            f"入力OK: name={form.name.data}, message={form.message.data}",
            "ok",
        )
        return redirect(url_for("index"))

    return render_template("validate_10_4.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
