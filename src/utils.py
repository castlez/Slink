
def fib(n):
    old = 0
    cur = 1
    i = 1
    yield cur
    while (i < n):
        cur, old, i = cur+old, cur, i+1
        yield cur