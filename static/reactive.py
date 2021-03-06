import random
import json
from lib.epochdate import datetimeargs2epoch

current_call = None
execute = []


def consume():
    while execute:
        call = execute.pop()
        call()


def reactive(model, func, node=None, template=None):
    def helper():
        global current_call
        model.reset(helper)
        current_call = helper
        func(model, node, template)
        current_call = None

    helper()


class Model(object):
    def __init__(self, id, **kw):
        if id is None:
            id = str(random.random())
        self.__dict__['_dep'] = []
        self.__dict__['_dirty'] = set()
        self.__dict__['id'] = id
        self.__dict__['__collection__'] = self.__class__.__name__
        for k,v in kw.items():
            if k in ('__deleted__', '__collection__'):
                continue
            setattr(self, k, v)

        self.__class__.objects[id] = self

    def validate(self):
        return all([getattr(self, m)() for m in dir(self.__class__) if m.startswith('validate_')])

    def save(self):
        if len(self._dirty) == 0:
            return
        dct = {}
        for k in self._dirty:
            dct[k] = getattr(self, k)
        data = {'id': self.id, '__collection__': self.__collection__}
        data.update(dct)
        self._dirty = set()
        print ('*** sending data', data)
        data = datetimeargs2epoch(data)
        Model.ws.send(json.dumps(data))

    def reset(self, func):
        print ('reset', func)
        self._dep = [item for item in self._dep if item['call'] != func]

    def __getattr__(self, name):
        if current_call is not None:
            self._dep.append({'call': current_call, 'attr': name})
        return self.__dict__['_'+name]

    def __setattr__(self, key, value):
        print('__setattr__')
        if key.startswith('_'):
            dirty = False
            key = key[1:]
        else:
            dirty = True

        if '_'+key not in self.__dict__.keys():
            self.__dict__['_'+key] = value
            if dirty:
                self._dirty.add(key)
            print('seteamos sin append execute')
            return

        if value != self.__dict__['_'+key]:
            print('value es != a current value')
            self.__dict__['_'+key] = value
            if dirty:
                self._dirty.add(key)
            global execute

            for item in self._dep:
                if item['attr'] == key and item['call'] not in execute:
                    print('append to execute model.id', self.id, key, value)
                    execute.append(item['call'])
