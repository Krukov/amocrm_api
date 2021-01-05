from datetime import datetime, timedelta
from typing import Optional, Union

from .. import exceptions
from ..interaction import BaseInteraction
from .user import User


class Direction:
    INBOUND = "inbound"
    OUTBOUNT = "outbound"


class Status:
    LEAVE_MESSAGE = 1  #  оставил сообщение
    CALL_LATER = 2  #  перезвонить позже
    OUT_OFF = 3  #  нет нa месте
    SUCCESS = 4  #  разговор состоялся
    WRONG_NUMBER = 5  #  неверный номер
    UNAVAILABLE = 6  #  Не дозвонился
    BUSY = 7  # номер занят


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
        created_by: Union[None, User, int] = None,
        updated_by: Union[None, User, int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        **kwargs
    ):
        if created_by:
            if isinstance(created_by, User):
                created_by = created_by.id
            kwargs["created_by"] = created_by
        if updated_by:
            if isinstance(updated_by, User):
                updated_by = updated_by.id
            kwargs["updated_by"] = updated_by
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
        if created_at:
            data["created_at"] = created_at.timestamp()
        if created_at:
            data["updated_at"] = updated_at.timestamp()
        response, status_ = self.request("post", "calls", data=[data])
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
