def simple_decorator(func):
    def wrapper():
        print("処理を開始します")
        func()
        print("処理を終了します")
    return wrapper

@simple_decorator
def say_hello():
    print("こんにちは")

say_hello()
