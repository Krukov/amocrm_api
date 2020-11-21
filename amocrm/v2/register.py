class _RegisterMeta(type):
    _REGISTER = {}

    def __new__(cls, name, bases, dct):
        _class = super().__new__(cls, name, bases, dct)
        cls._REGISTER[name] = _class
        return _class

    @classmethod
    def get_model_by_name(cls, name):
        return cls._REGISTER.get(name)


def get_model_by_name(name):
    return _RegisterMeta.get_model_by_name(name)
