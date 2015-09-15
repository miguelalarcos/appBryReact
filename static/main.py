from browser import document, html, websocket
import json
import random
from reactive import Model, execute
from controller import Controller
from filters import filters

DIV = html.DIV


def consume():
    while execute:
        call = execute.pop()
        call()


class A(Model):
    objects = {}

    def __init__(self, id, x):
        if id is None:
            id = str(random.random())
        super(A, self).__init__(id)
        self.x = x
        A.objects[id] = self


collections = {}
collections['A'] = A
filter = filters['0'](x=5, y=10)
#filter = {'x': {"$gt": 5, "$lt": 10}}


def hello(model, node):
    node.text = model.x

container = DIV('container')
controllers = [Controller(key='x', filter=filter, node=container, func=hello)]
document <= container
# ##############


def on_message(evt):
    result = evt.data
    data = json.loads(result)
    collection = data.pop('__collection__')
    klass = collections[collection]
    print 'buscamos si ya tenemos el objeto con id', data['id']
    try:
        model = klass.objects[data['id']]
        print 'encontrado'
    except KeyError:
        model = klass(**data)
        print 'nuevo'

    if all([c.test(model, data) for c in controllers]):
        print 'eliminamos obj de cache'
        del klass.objects[model.id]
    else:
        for k, v in data.items():
            setattr(model, k, v)

    print klass.objects
    print 'consume'
    consume()

ws = websocket.WebSocket("ws://127.0.0.1:8888/ws")
ws.bind('message',on_message)

button_send = html.BUTTON()
button_send.text = 'send random data'
document <= button_send


def send_data():
    ws.send(json.dumps({'id': random.choice(['0', '1', '2']), '__collection__': 'A', 'x': random.randint(0, 10)}))

button_send.bind('click', send_data)
ws.send(json.dumps({'x': 5, 'y': 10, '__filter__': '0'}))
