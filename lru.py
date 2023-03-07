import math
import random

r = random.randrange(1, 3)
r1 = random.random()
r2 = r + r1
prob = ()


def lru_cache(cycle_len):
    n = int(cycle_len - cycle_len // 10 * r2)

    def wrapper2(func):
        def wrapper(key, state1, state2, i, round):
            if cycle_len < 255 or round > 1:
                return func(key, state1, state2, i, round)
            if n == i:
                state1 = state1[:]
                state1[1] = int(key[:8])
                state2 = state1[:]
                state2[1] = int(key[:8])
                print(f'Состояние 1: {state1}')
                print(f'Состояние 2: {state2}')
                return key[:8]
            else:
                return func(key, state1, state2, i, round)
        return wrapper
    return wrapper2
