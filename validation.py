from static.models import *


def validate(raw):
    collection = raw.pop('__collection__')
    klass = models[collection]
    model = klass(**raw)
    return model.validate()
