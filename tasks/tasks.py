tasks = {}


def task(func):
    tasks[func.__name__] = func
    return func


@task
def console(x):
    print ('>x: ', x)

