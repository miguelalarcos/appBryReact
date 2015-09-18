tasks = {}


class DB(object):
    def __init__(self, db, collection):
        self.db = db
        self.collection = collection

    def find(self, parameters):
        items = yield self.db[self.collection].find(parameters)
        for item in items:
            yield item.update({'__collection__': self.collection})

    def find_one(self, id):
        item = yield self.db[self.collection].find_one({'_id': id})
        yield item.update({'__collection__': self.collection})


def task(func):
    tasks[func.__name__] = func
    return func


@task
def plus_10_A(db, queue, id):
    db = DB(db, 'A')
    data = db.find_one({'_id': id})
    data['x'] += 10
    queue.put(data)
