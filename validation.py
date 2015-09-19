from static.models import *
from static.reactive import Model

klasses = {k: v for k, v in globals() if issubclass(v, Model)}


def validate(raw):
    collection = raw.pop('__collection__')
    klass = klasses[collection]
    model = klass(**raw)
    return model.validate()
