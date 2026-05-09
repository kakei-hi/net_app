import time

def measure_time(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"実行時間: {elapsed:.6f} 秒")
        return result
    
    return wrapper


@measure_time
def run_task(n):
    total = 0
    for i in range(n):
        total += i * i
    return total


@measure_time
def wait_task(seconds):
    time.sleep(seconds)
    return "done"

run_task(300000)  # 実行時間が表示される
wait_task(0.5)    # 実行時間が表示される
