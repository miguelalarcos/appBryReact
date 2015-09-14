current_name = None
current_call = None
execute = []
map_ = {}


def reactive(model, func, node=None):
    def helper():
        global current_call, current_name
        current_name = func.__name__
        objects = map_.get(func.__name__, set())
        for obj in objects:
            obj.reset(func.__name__)
        map_[func.__name__] = set()
        current_call = helper
        return func(model, node)
    helper()


# base class Model. __getattr__ makes (marks) the current reactive function to be called when the attribute is set
class Model(object):
    def __init__(self, id):
        self.__dict__['_map'] = []
        self.__dict__['id'] = id

    def reset(self, name):
        print ('reset', name)
        self.__dict__['_map'] = [item for item in self._map if item['name'] != name]

    def __getattr__(self, name):
        if current_name is not None:
            map_[current_name].add(self)
            self._map.append({'name': current_name, 'call': current_call, 'attr': name})
        return self.__dict__['_'+name]

    def __setattr__(self, key, value):
        if '_'+key not in self.__dict__.keys():
            self.__dict__['_'+key] = value
            return

        if value != self.__dict__['_'+key]:
            self.__dict__['_'+key] = value
            global execute
            for item in self._map:
                if item['attr'] == key and item['call'] not in execute:
                    execute.append(item['call'])