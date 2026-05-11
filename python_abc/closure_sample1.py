count = 0


def make_counter():
    def counter():
        global count
        count += 1
        return count

    return counter


increment = make_counter()

print(increment())
print(increment())
print(increment())
