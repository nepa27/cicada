import time
from functools import wraps
from typing import Callable


def time_work_dec(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        res = func(*args, **kwargs)
        end_time = time.time()
        result_time = round(end_time - start_time, 2)

        print(f"Время выполнения программы: {result_time} сек.")
        return res

    return wrapper
