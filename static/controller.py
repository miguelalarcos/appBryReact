from lib.filter_mongo import pass_filter
from reactive import reactive
#from browser import html, window
import browser
#html = browser.html
window = browser.window
import random

jq = window.jQuery.noConflict(True)

#DIV = html.DIV


def makeDIV(id, model, func):
    node = jq("<div reactive_id='"+str(id)+"'>test</div>")
    name = func.__name__+str(random.random())
    reactive(model, func, node, name)
    return node


class Controller(object):
    controllers = []

    def __init__(self, key, filter, node, func, first=False):
        self.lista = []
        self.key = key
        self.filter = filter
        self.node = node
        self.func = func
        self.first = first
        self.__class__.controllers.append(self)

    def pass_filter(self, raw):
        return pass_filter(self.filter, raw)

    def test(self, model, raw):
        print('im in tst of node', self.node.id)

        if model.id in [x.id for x in self.lista]:
            print('esta dentro')
            if pass_filter(self.filter, raw):
                print('y permance dentro', 'MODIFY')
                # if not self.first:
                self.modify(model)
                return False
            else:
                print('y sale', 'OUT')
                self.out(model)
                return True
        else:
            print('esta fuera')
            if pass_filter(self.filter, raw):
                print('y entra', 'NEW')
                self.new(model)
                return False
            else:
                print('y permanece fuera')
                return True #False

    def new(self, model):
        tupla = self.indexInList(model)
        index = tupla[0]

        self.lista.insert(index, model)
        print('new: ', model, tupla)
        print([x.x for x in self.lista])
        action = tupla[1]
        if action == 'append':
            node = makeDIV(model.id, model, self.func)

            ref = jq('#'+str(self.node.id))
            ref.append(node)
        elif action == 'before':
            node = makeDIV(model.id, model, self.func)

            ref = jq('#'+str(self.node.id)).children("[reactive_id='"+str(tupla[2])+"']")

            ref.before(node)
            if self.first:
                ref.remove()
        elif action == 'after':
            if not self.first:
                node = makeDIV(model.id, model, self.func)

                ref = jq('#'+str(self.node.id)).children("[reactive_id='"+str(tupla[2])+"']")
                ref.after(node)

    def out(self, model):
        index = self.indexById(model.id)
        del self.lista[index]
        print ('out: ', model)

        node = jq('#'+str(self.node.id)).children("[reactive_id='"+str(model.id)+"']")
        node.remove()
        print('eliminado')
        if self.first and index == 0 and len(self.lista) > 0:
            node = makeDIV(self.lista[0].id, self.lista[0], self.func)
            ref = jq('#'+str(self.node.id))
            ref.append(node)

    def modify(self, model):
        index = self.indexById(model.id)
        del self.lista[index]
        tupla = self.indexInList(model)
        if index == tupla[0]:
            print('ocupa misma posicion')
        else:
            print('move to ', model, tupla)

            node = jq('#'+str(self.node.id)).children("[reactive_id='"+str(model.id)+"']")
            node.remove()
            action = tupla[1]
            if action == 'before':
                ref = jq('#'+str(self.node.id)).children("[reactive_id='"+str(tupla[2])+"']")
                ref.before(node)
            elif action == 'after':
                ref = jq('#'+str(self.node.id)).children("[reactive_id='"+str(tupla[2])+"']")
                ref.after(node)

        self.lista.insert(tupla[0], model)
        print([x.x for x in self.lista])

    def indexById(self, id):
        index = 0
        for item in self.lista:
            if item.id == id:
                break
            index += 1
        return index

    @staticmethod
    def compare(a, b, key, order='asc'):
        v_a = getattr(a, key)
        v_b = getattr(b, key)
        if v_a == v_b:
            return 0
        if v_a > v_b:
            if order == 'desc':
                return 1
            else:
                return -1
        if order == 'desc':
            return -1
        else:
            return 1

    def indexInList(self, model):
        if self.lista == []:
            return (0, 'append')

        index = 0
        print([x.x for x in self.lista])
        keys = self.key[:]
        key, order = keys.pop(0)
        flag = False
        for item in self.lista:
            while True:
                ret = Controller.compare(model, item, key, order)
                if ret == 1:
                    flag = True
                    break
                if ret == 0:
                    if len(keys):
                        key, order = keys.pop(0)
                    else:
                        flag = True
                        break
                else:
                    break
            if flag:
                break
            index += 1
        if index == 0:
            return (index, 'before', self.lista[0].id)
        else:
            return (index, 'after', self.lista[index-1].id)