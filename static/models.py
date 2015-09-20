from reactive import Model


class A(Model):
    objects = {}

    def validate_x(self):
        return type(self.x) == int and self.x < 100

models = {}
models['A'] = A
