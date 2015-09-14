from filter_mongo import pass_filter
from reactive import reactive
from browser import html
from pyquery import Selector

DIV = html.DIV


class Controller(object):
    controllers = []

    def __init__(self, key, filter, node, func):
        self.lista = []
        self.key = key
        self.filter = filter
        self.node = node
        self.func = func
        self.__class__.controllers.append(self)

    def pass_filter(self, raw):
        return pass_filter(self.filter, raw)

    def test(self, model, raw):
        if model.id in [x.id for x in self.lista]:
            print 'esta dentro'
            if pass_filter(self.filter, raw):
                print 'y permance dentro', 'MODIFY'
                self.modify(model)
                return False
            else:
                print 'y sale', 'OUT'
                self.out(model)
                return True
        else:
            print 'esta fuera'
            if pass_filter(self.filter, raw):
                print 'y entra', 'NEW'
                self.new(model)
                return False
            else:
                print 'y permanece fuera'
                return False

    def new(self, model):
        tupla = self.indexInList(model)
        index = tupla[0]
        self.lista.insert(index, model)
        print('new: ', model, tupla)
        node = DIV(model.id)
        reactive(model, self.func, node)
        action = tupla[1]
        if action == 'append':
            self.node.append(node)
        elif action == 'before':
            ref = Selector('#'+str(model.id), self.node).get()
            ref.before(node)
        elif action == 'after':
            ref = Selector('#'+str(model.id), self.node).get()
            ref.after(node)

    def out(self, model):
        index = self.indexById(model.id)
        del self.lista[index]
        print ('out: ', model)
        ref = Selector('#'+str(model.id), self.node).get()
        self.node.remove(ref)

    def modify(self, model):
        index = self.indexById(model.id)
        del self.lista[index]
        tupla = self.indexInList(model)
        if index == tupla[0]:
            print 'ocupa misma posicion'
        else:
            print 'move to ', model, tupla
            #
            node = Selector('#'+str(model.id), self.node).get()
            self.node.remove(node)
            #
            action = tupla[1]
            if action == 'before':
                ref = Selector('#'+str(tupla[2]), self.node).get()
                ref.before(node)
            elif action == 'after':
                ref = Selector('#'+str(tupla[2]), self.node).get()
                ref.after(node)
            #
        self.lista.insert(tupla[0], model)

    def indexById(self, id):
        index = 0
        for item in self.lista:
            if item.id == id:
                break
            index += 1
        return index

    def indexInList(self, model):
        if self.lista == []:
            return (0, 'append')
        v = getattr(model, self.key)
        index = 0
        for item in self.lista:
            if v <= getattr(item, self.key):
                break
            index += 1
        if index == 0:
            return (index, 'before', self.lista[0].id)
        else:
            return (index, 'after', self.lista[index-1].id)