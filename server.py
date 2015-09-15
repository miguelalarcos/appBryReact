from tornado import web, ioloop, websocket, gen
from tornado.queues import Queue
from static.lib.filter_mongo import pass_filter
import json
from static.filters import filters

q = Queue()
q_out = Queue()

mongo_model = {'A': {}}
mongo_model['A']['0'] = {'id': '0', 'x': 50}
mongo_model['A']['1'] = {'id': '1', 'x': 51}
mongo_model['A']['2'] = {'id': '2', 'x': 52}


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
        item = yield q_out.get()
        client = item[0]
        model = item[1]
        client.write_message(json.dumps(model))
        q_out.task_done()


@gen.coroutine
def consumer():
    global mongo_model
    while True:
        item = yield q.get()
        client = item.pop('__client__')
        if '__filter__' in item.keys():
            name = item.pop('__filter__')
            client.add_filter(name, filters[name](**item))
        else:
            #collection = item.pop('__collection__')
            collection = item['__collection__']
            model = item
            print 'get model id:', model['id']
            model_before = mongo_model[collection][model['id']]
            if '__deleted__' in model.keys():
                deleted = True
                print 'delete model'
            else:
                deleted = False
                if '__new__' in model.keys():
                    new = True
                    print 'new model'
                else:
                    new = False
                    print 'update model'
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
                            yield q_out.put((client, model))
                            break
                    else:
                        print 'send', client, model
                        yield q_out.put((client, model))
                        break
        q.task_done()


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
        yield q.put(item)

app = web.Application([
    (r"/", MainHandler),
    (r'/ws', SocketHandler),
    (r"/static/(.*)", web.StaticFileHandler, {"path": "/home/miguel/development/brython/app/static/"}),
])


if __name__ == '__main__':
    app.listen(8888)
    ioloop.IOLoop.current().spawn_callback(consumer)
    ioloop.IOLoop.current().spawn_callback(sender)
    ioloop.IOLoop.instance().start()



