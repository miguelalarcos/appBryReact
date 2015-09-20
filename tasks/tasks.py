from base import task


@task
def plus_10_A(db, queue, id):
    data = db['A'].find_one({'_id': id})
    data['x'] += 10
    queue.put(data)
