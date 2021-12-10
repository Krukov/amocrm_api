import datetime


class Filter:
    def __init__(self, name):
        self._name = name

    def _as_params(self):
        return {}


class SingleFilter(Filter):
    def __call__(self, value):
        self._value = value
        return self

    def _as_params(self):
        return {"filter[{}]".format(self._name): self._value}


class SingleListFilter(Filter):
    def __call__(self, value):
        self._value = value
        return self

    def _as_params(self):
        return {"filter[{}][]".format(self._name): self._value}


class MultiFilter(Filter):
    def __call__(self, values):
        self._values = values
        return self

    def _as_params(self):
        return {"filter[{}][0]".format(self._name): self._values}


class RangeFilter(Filter):
    def __call__(self, value_from, value_to):
        self._value_from = value_from
        self._value_to = value_to
        return self

    def _as_params(self):
        return {
            "filter[{}][from]".format(self._name): self._value_from,
            "filter[{}][to]".format(self._name): self._value_to,
        }


class DateRangeFilter(RangeFilter):
    def __call__(self, value_from: datetime.datetime, value_to: datetime.datetime):
        self._value_from = int(value_from.timestamp())
        self._value_to = int(value_to.timestamp())
        return self
