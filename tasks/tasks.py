from base import DB, task


@task
def plus_10_A(db, queue, id):
    db = DB(db, 'A')
    data = db.find_one({'_id': id})
    data['x'] += 10
    queue.put(data)
