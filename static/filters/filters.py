from base import filter


@filter('A')
def my_filter(x, y):
    return {'x': {"$gt": x, "$lt": y}}
