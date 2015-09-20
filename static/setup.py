from browser import document, html, window
import javascript
from lib.epochdate import epochargs2datetime

WebSocket = javascript.JSConstructor(window.WebSocket)

import json
from reactive import Model, consume
from controller import Controller
from models import *

jq = window.jQuery.noConflict(True)

collections = {}


def setup_eachs():
    eachs = jq('[each]')
    for each in eachs:
        c = Controller.controllers[each.attr('each')]
        c.node = each

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

        if all([c.test(model, data) for c in Controller.controllers.values()]):
            print('eliminamos obj de cache')
            del klass.objects[model.id]

        print('consume')
        consume()
    except Exception as e:
        print ('******************** error', e)


def init():
    ws = WebSocket("ws://127.0.0.1:8888/ws")
    Model.ws = ws
    Controller.ws = ws

    global collections
    for name, klass in globals().items():
        try:
            if issubclass(klass, Model):
                collections[name] = klass
        except:
            pass

    ws.bind('message', on_message)




