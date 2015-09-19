from reactive import Model, autosuper


@autosuper
class A(Model):

    def validate_x(self):
        return type(self.x) == int and self.x < 100


