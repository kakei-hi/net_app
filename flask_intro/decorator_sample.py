# # Flask本格入門 list2.3
# def a():
#     print(" Aです")

# # 関数の実行
# a()

# # Flask本格入門 list2.6
# def outer(func):
#     def inner():
#         print("inner関数が呼び出されました")
#         func()
#     return inner

# # 関数a
# @outer
# def a():
#     print("Aです")

# # 関数b
# @outer
# def b():
#     print("Bです")

# # 関数の実行
# a()
# b()

# Flask本格入門 list2.7
def outer(func):
    def inner(*args, **kwargs):
        print("inner関数が呼び出されました")
        func(*args, **kwargs)
    return inner

# タプルを引数にする関数
nums = (10, 20, 30, 40)
@outer
def show_nums(nums):
    sum = 0
    for num in nums:
        sum += num
    print(f"合計: {sum}")

# 辞書を引数にする関数
users = {"氏名": "山田太郎", "年齢": 30}
@outer
def show_users(users):
    for key, value in users.items():
        print(f"{key}: {value}")

# 関数の実行
show_nums(nums)
show_users(users)
