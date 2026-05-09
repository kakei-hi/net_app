x = 5
def func1():
    x = 10
    print(f"関数の中:{x}")

func1() 
print(f"関数の外:{x}")

def func2():
    global x
    x = 20
    print(f"関数の中:{x}")

func2()
print(f"関数の外:{x}")
