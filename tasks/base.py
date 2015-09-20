from tornado import gen
tasks = {}


def task(func):
    func = gen.coroutine(func)
    tasks[func.__name__] = func
    return func

