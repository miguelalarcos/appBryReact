from tornado import web, ioloop, websocket, gen
from tornado.queues import Queue
from static.lib.filter_mongo import pass_filter
import json
from static.filters.filters import filters
import motor

db = motor.MotorClient().test_database

q_mongo = Queue()
q_send = Queue()


class Client(object):
    clients = {}

    def __init__(self, socket):
        self.socket = socket
        self.filters = {}
        Client.clients[socket] = self

    def add_filter(self, name, filter):
        self.filters[name] = filter

    @classmethod
    def remove_client(cls, client):
        cls.clients.remove(client)
        del Client.clients[client.socket]

@gen.coroutine
def sender():
    while True:
        print('yield: q_send.get()')
        item = yield q_send.get()
        client = item[0]
        model = item[1]
        print('yield: client.write', json.dumps(model))
        x = client.write_message(json.dumps(model))
        print ('*******************', x)
        q_send.task_done()


@gen.coroutine
def mongo_consumer():

    while True:
        print('yield: q_mongo.get()')
        item = yield q_mongo.get()
        print('item from queue', item)
        client_socket = item.pop('__client__')
        client = Client.clients[client_socket]
        if '__filter__' in item.keys():
            name = item.pop('__filter__')
            client.add_filter(name, filters[name](**item))
        else:
            collection = item['__collection__']
            model = item

            new = False
            deleted = False
            print('future')
            future = db[collection].find_one({'_id': model['id']})
            print('buscamos model before')
            model_before = yield future
            print('model before', model_before)
            if model_before is None:
                model_id = model.copy()
                model_id['_id'] = model_id['id']
                del model_id['id']
                print('yield insert')
                yield db[collection].insert(model_id)
                new = True
            elif '__deleted__' in model.keys():
                deleted = True
                print('yield remove')
                yield db[collection].remove({'_id': model['id']})
            else:
                model_copy = model.copy()
                del model_copy['id']
                print('yield update')
                yield db[collection].update({'_id': model['id']}, model_copy)

            for client in Client.clients.values():
                for filt in client.filters.values():
                    print('filter:', filt)
                    if filt['__collection__'] != collection:
                        continue
                    before = (not new) and pass_filter(filt, model_before)
                    print('before:', before)

                    if not before and not deleted:
                        after = pass_filter(filt, model)
                        print('after:', after)
                        if after:
                            print('send', client.socket, model)
                            yield q_send.put((client.socket, model))
                            break
                    else:
                        print('send', client.socket, model)
                        yield q_send.put((client.socket, model))
                        break
        q_mongo.task_done()


class MainHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")


class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        Client(self)

    def close(self):
        Client.remove_client(self)

    @gen.coroutine
    def on_message(self, message):
        print('***', message)
        item = json.loads(message)
        item['__client__'] = self
        print('yield: q_mongo.put()')
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



