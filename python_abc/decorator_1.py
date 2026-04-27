def decorator(func):
    def wrapper(*args, **kwargs):
       print("処理前")
       print(func(*args, **kwargs))
       print("処理後")
    return wrapper

@decorator
def add(a, b):
    return a + b

add(2, 3)
