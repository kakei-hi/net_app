import os

from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
# セッション機能のために必要（本番では環境変数で設定する）
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-only")


@app.route("/", methods=["GET", "POST"])
def form_page():
    """入力画面。POST 時に値をセッションへ保存して表示画面へ遷移する。"""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        message = request.form.get("message", "").strip()

        session["name"] = name
        session["message"] = message
        session["access_count"] = session.get("access_count", 0) + 1

        return redirect(url_for("result_page"))

    return render_template("session_10_1_from.html")


@app.route("/to", methods=["GET"])
def result_page():
    """セッションから値を読み出して表示する画面。"""
    name = session.get("name", "")
    message = session.get("message", "")
    access_count = session.get("access_count", 0)

    return render_template(
        "session_10_1_to.html",
        name=name,
        message=message,
        access_count=access_count,
    )


@app.route("/clear", methods=["POST"])
def clear_session():
    """学習用にセッションを初期化する。"""
    session.clear()
    return redirect(url_for("form_page"))


if __name__ == "__main__":
    app.run(debug=True)
