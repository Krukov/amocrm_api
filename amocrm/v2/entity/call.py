from typing import Optional, Union
from datetime import timedelta

from .. import exceptions
from ..interaction import BaseInteraction


class Direction:
    inbound = "inbound"
    outbound = "outbound"


class Status:
    LEAVE_MESSAGE = 1 #  оставил сообщение
    CALL_LATER = 2 #  перезвонить позже
    OUT_OFF = 3 #  нет нa месте
    SUCCESS = 4 #  разговор состоялся
    WRONG_NUMBER = 5 #  неверный номер
    UNAVAILABLE = 6 #  Не дозвонился
    BUSY = 7 #  номер занят


class Call(BaseInteraction):

    def create(
        self,
        direction: str,
        phone: str,
        source: str,
        duration: Union[int, timedelta],
        uniq: Optional[str] = None,
        link: Optional[str] = None,
        result: Optional[str] = None,
        status: Optional[str] = None,
        **kwargs
    ):
        if isinstance(duration, timedelta):
            duration = duration.total_seconds()
        data = {
            "phone": phone,
            "source": source,
            "duration": duration,
            "uniq": uniq,
            "link": link,
            "call_status": status,
            "call_result": result,
            "direction": direction,
            **kwargs,
        }
        response, status_ = self.request("post", "call", data=[data])
        if status_ == 400:
            raise exceptions.ValidationError(response)
        return response["_embedded"]["calls"][0]

    def get(self, *args, **kwargs):
        raise NotImplemented()

    def get_list(self, *args, **kwargs):
        raise NotImplemented()

    def get_all(self, *args, **kwargs):
        raise NotImplemented()

    def update(self, *args, **kwargs):
        raise NotImplemented()
