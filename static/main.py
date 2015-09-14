from browser import document, html, websocket
import json
import random
from reactive import Model, execute
from controller import Controller

DIV = html.DIV


def consume():
    while execute:
        call = execute.pop()
        call()


class A(Model):
    objects = {}

    def __init__(self, id, x):
        super(A, self).__init__(id)
        self.x = x
        A.objects[id] = self


filter = {'x': {"$gt": 7, "$lt": 10}}


def hello(model, node):
    node.text = model.x

container = DIV('container')
controllers = [Controller(key='x', filter=filter, node=container, func=hello)]
document <= container
# ##############


def on_message(evt):
    result = evt.data
    data = json.loads(result)
    print 'buscamos si ya tenemos el objeto con id', data['id']
    try:
        model = A.objects[data['id']]
        print 'encontrado'
    except KeyError:
        model = A(**data)
        print 'nuevo'

    if all([c.test(model, data) for c in controllers]):
        print 'eliminamos obj de cache'
        del A.objects[model.id]
    else:
        for k, v in data.items():
            setattr(model, k, v)

    print A.objects
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
ws.send(json.dumps({'x': 0, 'y': 10, '__filter__': '0'}))
