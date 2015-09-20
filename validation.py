from static.models import models


def validate(raw):
    collection = raw.pop('__collection__')
    klass = models[collection]
    model = klass(**raw)
    return model.validate()
