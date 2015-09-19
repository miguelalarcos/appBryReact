filters = {}


def filter(collection):
    def helper1(func):
        filters[func.__name__] = func

        def helper2(**kw):
            kw['__collection__'] = collection
            return func(**kw)
        return helper2
    return helper1

