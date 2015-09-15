filters = {}
filters['0'] = lambda x, y: {'__collection__': 'A', 'x': {"$gt": x, "$lt": y}}
