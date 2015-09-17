def pass_filter(filter, model):
    print('model en pass_filter', model)
    if '__deleted__' in model.keys():
        return False
    for key, value in filter.items():
        if key == '__collection__':
            continue
        if type(value) == int or type(value) == str:
            if model[key] != value:
                return False
        else:
            for op, val in value.items():
                if op == '$gt':
                    if model[key] <= val:
                        return False
                elif op == '$lt':
                    if model[key] > val:
                        return False
    return True

