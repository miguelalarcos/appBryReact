from browser import document, html, window # , websocket
import javascript
from lib.epochdate import epochargs2datetime

WebSocket = javascript.JSConstructor(window.WebSocket)

import json
import random
from reactive import Model, consume
from controller import Controller
from filters import filters
from models import A

jq = window.jQuery.noConflict(True)

DIV = html.DIV

ws = WebSocket("ws://127.0.0.1:8888/ws")
Model.ws = ws


collections = {}
collections['A'] = A
filter = filters['my_filter'](x=5, y=10)

container = jq('#container')

first = jq('#first')

controllers = [Controller(key=[('x', 'desc')], filter=filter, node=container),
               Controller(key=[('x', 'desc')], filter=filter, node=first, first=True)]

# ##############


def on_message(evt):
    try:
        result = evt.data
        print('raw', result)
        data = json.loads(result)
        data = epochargs2datetime(data)
        collection = data.pop('__collection__')
        klass = collections[collection]
        print('buscamos si ya tenemos el objeto con id', data['id'])
        try:
            model = klass.objects[data['id']]
            print('encontrado')
            for k, v in data.items():
                if k in ('id', '__deleted__'):
                    continue
                print ('set model.id', data['id'], k, v)
                setattr(model, '_'+k, v)
        except KeyError:
            print('nuevo')
            data_ = {}
            for k, v in data.items():
                if not k.startswith('_') and k != 'id':
                    data_['_'+k] = v
                else:
                    data_[k] = v
            model = klass(**data_)

        if all([c.test(model, data) for c in controllers]):
            print('eliminamos obj de cache')
            del klass.objects[model.id]

        print('consume')
        consume()
    except Exception as e:
        print ('******************** error', e)


# ws = WebSocket("ws://127.0.0.1:8888/ws")
ws.bind('message', on_message)

#button_send = html.BUTTON()
#button_send.text = 'send random data'
#document <= button_send

button_send = jq('#button')


sent_initial_data = False


def send_data():
    global sent_initial_data
    if not sent_initial_data:
        ws.send(json.dumps({'x': 5, 'y': 10, '__filter__': 'my_filter'}))
        sent_initial_data = True
    try:
        if random.random() < 0.5:
            obj = A(None, x=random.randint(0, 10))
        else:
            obj = random.choice(list(A.objects.values()))
            print('*** random choice object')
            obj.x = random.randint(0, 10)
    except Exception as e:
        print ('-----------error:', e)
        obj = A(None, x=random.randint(0, 10))
    obj.save()


button_send.bind('click', send_data)

