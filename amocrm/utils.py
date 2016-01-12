# -*- coding: utf-8 -*-

__all__ = ['lazy_dict_property', 'lazy_property']


empty = type('empty', (), {})


class lazy_property(object):

    def __init__(self, calculate_function):
        self._calculate = calculate_function

    def __get__(self, obj, _=None):
        if obj is None:
            return self
        value = self._calculate(obj)
        if value is not None:
            setattr(obj, self._calculate.__name__, value)
        return value


class lazy_dict_property(object):

    def __init__(self, calculate_function):
        self.__delegate()
        self.fake = empty()
        self.fake._calculate = calculate_function

    def __get__(self, obj, _=None):
        self.fake._obj = obj
        return self.fake

    def __delegate(self):
        for method_name in dict.__dict__.keys():
            if hasattr(empty, method_name):
                continue
            meth = self.__dispatch(method_name)
            setattr(empty, method_name, meth)

    @staticmethod
    def __dispatch(name):
        def __wrapper(*args, **kwargs):
            this = args[0]
            value = this._calculate(this._obj)
            setattr(this._obj, this._calculate.__name__, value)
            return getattr(value, name)(*args[1:], **kwargs)
        return __wrapper


class User(object):
    def __init__(self, data):
        assert isinstance(data, dict)
        self.__data = data
        self.id = data['id']
        self.login, self.name = data.get('login'), data.get('name')
        self.phone = data.get('phone')

    def __repr__(self):
        return 'User(%s)' % self.__data

    @classmethod
    def get_one(cls, array, values):
        filter_func = lambda _: _.login in values or _.name in values or _.id in values
        match = [user for user in array if filter_func(user)]
        return match.pop() if match else None