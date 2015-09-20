from browser import window
import random
from controller import Controller
from models import A
from setup import init, setup_eachs

init()

jq = window.jQuery.noConflict(True)

key = [('x', 'desc')]
filter = ('my_filter', {'x': 5, 'y': 10})
Controller('MyController', key, filter)
Controller('MyController2', key, filter, first=True)

setup_eachs()

button_send = jq('#button')
sent_initial_data = False


def send_data():
    global sent_initial_data
    if not sent_initial_data:
        Controller.subscribe_all()
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


