from tornado import web, ioloop, websocket, gen
from tornado.queues import Queue
from static.lib.filter_mongo import pass_filter
import json
from static.filters import filters
import motor

db = motor.MotorClient().test_database

q_mongo = Queue()
q_send = Queue()


class Client(object):
    clients = []

    def __init__(self, socket):
        self.socket = socket
        self.filters = {}
        Client.clients.append(self)

    def add_filter(self, name, filter):
        self.filters[name] = filter

    @classmethod
    def remove_client(cls, client):
        cls.clients.remove(client)

@gen.coroutine
def sender():
    while True:
        item = yield q_send.get()
        client = item[0]
        model = item[1]
        yield client.write_message(json.dumps(model))
        q_send.task_done()


@gen.coroutine
def mongo_consumer():
    global mongo_model
    while True:
        item = yield q_mongo.get()
        client = item.pop('__client__')
        if '__filter__' in item.keys():
            name = item.pop('__filter__')
            client.add_filter(name, filters[name](**item))
        else:
            collection = item['__collection__']
            model = item

            new = False
            deleted = False
            model_before = yield db[collection].find_one({'_id': model['id']})
            if model_before is None:
                yield db[collection].insert(model)
                new = True
            elif '__deleted__' in model.keys():
                deleted = True
                yield db[collection].remove({'_id': model['id']})
            else:
                model_copy = model.copy()
                del model_copy['id']
                yield db[collection].update({'_id': model['id']}, model_copy)
                mongo_model[collection][model['id']] = model

            for client in Client.clients:
                for filt in client.filters:
                    print('filter:', filt)
                    if filt['__collection__'] != collection:
                        continue
                    before = (not new) and pass_filter(filt, model_before)
                    print 'before:', before

                    if not before and not deleted:
                        after = pass_filter(filt, model)
                        print 'after:', after
                        if after:
                            print 'send', client, model
                            yield q_send.put((client, model))
                            break
                    else:
                        print 'send', client, model
                        yield q_send.put((client, model))
                        break
        q_mongo.task_done()


class MainHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")


class SocketHandler(websocket.WebSocketHandler):
    def open(self):
        Client(self)

    def close(self):
        Client.remove_client(self)

    @gen.coroutine
    def on_message(self, message):
        print('***', message)
        item = json.loads(message)
        item['__client__'] = self
        yield q_mongo.put(item)

app = web.Application([
    (r"/", MainHandler),
    (r'/ws', SocketHandler),
    (r"/static/(.*)", web.StaticFileHandler, {"path": "/home/miguel/development/brython/app/static/"}),
])


if __name__ == '__main__':
    app.listen(8888)
    ioloop.IOLoop.current().spawn_callback(mongo_consumer)
    ioloop.IOLoop.current().spawn_callback(sender)
    ioloop.IOLoop.instance().start()



