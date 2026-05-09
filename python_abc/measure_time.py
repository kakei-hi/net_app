from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable


def measure_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that measures and prints execution time of a function."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.6f} seconds")
        return result

    return wrapper


@measure_time
def run_task(n: int) -> int:
    total = 0
    for i in range(n):
        total += i * i
    return total


@measure_time
def wait_task(seconds: float) -> str:
    time.sleep(seconds)
    return "done"


if __name__ == "__main__":
    print(run_task(300000))
    print(wait_task(0.5))
