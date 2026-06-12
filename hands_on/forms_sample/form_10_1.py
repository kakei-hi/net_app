from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    """入力画面と送信後の表示画面を兼ねる GET 画面。"""
    name = request.args.get("name", "")
    message = request.args.get("message", "")
    submitted = bool(name or message)
    return render_template(
        "PRG_10_1.html",
        name=name,
        message=message,
        submitted=submitted,
    )


@app.route("/submit", methods=["POST"])
def submit():
    """フォームの内容を受け取り、GET 画面へリダイレクトする。"""
    name = request.form.get("name", "").strip()
    message = request.form.get("message", "").strip()

    # PRG (Post-Redirect-Get): POST のあとに redirect することで、
    # ブラウザの再読み込みによる二重送信を避けられる。
    return redirect(url_for("index", name=name, message=message))


if __name__ == "__main__":
    app.run(debug=True)
