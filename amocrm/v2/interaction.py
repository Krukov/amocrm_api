import requests

from . import exceptions
from .tokens import default_token_manager

_session = requests.Session()


class BaseInteraction:
    _default_headers = {
        "User-Agent": "amocrm-py/v2",
    }

    def __init__(self, token_manager=default_token_manager, session=_session, headers=_default_headers):
        self._token_manager = token_manager
        self._session = session
        self._default_headers = headers

    def get_headers(self):
        headers = {}
        headers.update(self._default_headers)
        headers.update(self._get_auth_headers())
        return headers

    def _get_auth_headers(self):
        return {"Authorization": "Bearer " + self._token_manager.get_access_token()}

    def _get_url(self, path):
        return "https://{subdomain}.amocrm.ru/api/v4/{path}".format(subdomain=self._token_manager.subdomain, path=path)

    def _request(self, method, path, data=None, params=None, headers=None):
        headers = headers or {}
        headers.update(self.get_headers())
        response = self._session.request(method, url=self._get_url(path), json=data, params=params, headers=headers)
        if response.status_code == 204:
            return None, 204
        if response.status_code < 300 or response.status_code == 400:
            return response.json(), response.status_code
        if response.status_code == 401:
            raise exceptions.UnAuthorizedException()
        if response.status_code == 403:
            raise exceptions.PermissionsDenyException()
        if response.status_code == 402:
            raise ValueError("Тариф не позволяет включать покупателей")
        raise exceptions.AmoApiException("Wrong status {} ({})".format(response.status_code, response.text))

    def request(self, method, path, data=None, params=None, headers=None, include=None):
        params = params or {}
        if include:
            params["with"] = ",".join(include)
        return self._request(method, path, data=data, params=params, headers=headers)

    def _list(self, path, page, include=None, limit=250, query=None, filters=(), order=None):
        assert order is None or len(order) == 1
        assert limit <= 250
        params = {
            "page": page,
            "limit": limit,
            "query": query,
        }
        if order:
            field, value = list(order.items())[0]
            params["order[{}]".format(field)] = value
        for _filter in filters:
            params.update(_filter._as_params())
        return self.request("get", path, params=params, include=include)

    def _all(self, path, include=None, query=None, filters=(), order=None, limit=250):
        page = 1
        while True:
            response, _ = self._list(
                path, page, include=include, query=query, filters=filters, order=order, limit=limit
            )
            if response is None:
                return
            yield response["_embedded"]
            if len(response["_embedded"]) != limit:
                return
            if "next" not in response["_links"]:
                return
            page += 1


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


class GenericInteraction(BaseInteraction):
    path = ""
    field = None

    def __init__(self, *args, path=None, field=None, **kwargs):
        super().__init__(*args, **kwargs)
        if path is not None:
            self.path = path
        if field is not None:
            self.field = field

    def _get_field(self):
        return self.field or self.path

    def _get_path(self):
        return self.path

    def get_list(self, page, include=None, limit=250, query=None, filters=None, order=None):
        response, _ = self._list(
            self._get_path(), page, include=include, limit=limit, query=query, filters=filters, order=order
        )
        return response["_embedded"][self._get_field()]

    def get_all(self, include=None, query=None, filters=(), order=None):
        for data in self._all(self._get_path(), include=include, query=query, filters=filters, order=order):
            yield from data[self._get_field()]

    def get(self, object_id, include=None):
        path = "{}/{}".format(self._get_path(), object_id)
        response, status = self.request("get", path, include=include)
        if status == 204:
            raise exceptions.NotFound()
        return response

    def create(self, data):
        response, status = self.request("post", self._get_path(), data=[data])
        if status == 400:
            raise exceptions.ValidationError(response)
        return response["_embedded"][self._get_field()][0]

    def update(self, object_id, data):
        path = "{}/{}".format(self._get_path(), object_id)
        response, status = self.request("patch", path, data=data)
        if status == 400:
            raise exceptions.ValidationError(response)
        return response
