import random

current_name = None
current_call = None
execute = []
map_ = {}


def consume():
    while execute:
        call = execute.pop()
        print('call()')
        call()


def reactive(model, func, node=None, func_name=''):
    def helper():
        global current_call, current_name
        current_name = func_name #func.__name__
        objects = map_.get(func_name) #func.__name__)
        if objects is None:
            objects = set()
        for obj in objects:
            obj.reset(func_name) #func.__name__)
        #map_[func.__name__] = set()
        map_[func_name] = set()
        current_call = helper
        return func(model, node)
    helper()


# base class Model. __getattr__ makes (marks) the current reactive function to be called when the attribute is set
class Model(object):
    def __init__(self, id):
        if id is None:
            id = str(random.random())
        self.__dict__['_map'] = []
        self.__dict__['id'] = id

        self.__class__.objects[id] = self

    def reset(self, name):
        print ('reset', name)
        #return
        self.__dict__['_map'] = [item for item in self._map if item['name'] != name]

    def __getattr__(self, name):
        if current_name is not None:
            map_[current_name].add(self)
            self._map.append({'name': current_name, 'call': current_call, 'attr': name})
        return self.__dict__['_'+name]

    def __setattr__(self, key, value):
        print('__setattr__')
        if '_'+key not in self.__dict__.keys():
            self.__dict__['_'+key] = value
            print('seteamos sin append execute')
            return

        if value != self.__dict__['_'+key]:
            print('value es != a current value')
            self.__dict__['_'+key] = value
            global execute
            print('self._map', self._map)
            for item in self._map:
                if item['attr'] == key and item['call'] not in execute:
                    print('append to execute model.id', self.id, key, value)
                    execute.append(item['call'])
