class Filter:
    def __init__(self, name):
        self._name = name

    def _as_params(self):
        return {}


class SingleFilter(Filter):
    def __call__(self, value):
        self._value = value

    def _as_params(self):
        return {"filter[{}]".format(self._name): self._value}


class SingleListFilter(Filter):
    def __call__(self, value):
        self._value = value

    def _as_params(self):
        return {"filter[{}][]".format(self._name): self._value}


class MultiFilter(Filter):
    def __call__(self, values):
        self._values = values

    def _as_params(self):
        return {"filter[{}][0]".format(self._name): self._values}


class RangeFilter(Filter):
    def __call__(self, value_from, value_to):
        self._value_from = value_from
        self._value_to = value_to

    def _as_params(self):
        return {
            "filter[{}][from]".format(self._name): self._value_from,
            "filter[{}][to]".format(self._name): self._value_to,
        }
