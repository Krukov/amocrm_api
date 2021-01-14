import logging
import os
from datetime import datetime
from typing import Optional, Tuple

import jwt
import requests

from . import exceptions

logger = logging.getLogger(__name__)


class TokensStorage:
    def get_access_token(self) -> Optional[str]:
        pass

    def get_refresh_token(self) -> Optional[str]:
        pass

    def save_tokens(self, access_token: str, refresh_token: str):
        pass


class MemoryTokensStorage(TokensStorage):
    def __init__(self):
        self._access_token = None
        self._refresh_token = None

    def get_access_token(self) -> Optional[str]:
        return self._access_token

    def get_refresh_token(self) -> Optional[str]:
        return self._refresh_token

    def save_tokens(self, access_token: str, refresh_token: str):
        self._access_token, self._refresh_token = access_token, refresh_token


class FileTokensStorage(TokensStorage):
    def __init__(self, directory_path=os.getcwd()):
        self._access_token_path = os.path.join(directory_path, "access_token.txt")
        self._refresh_token_path = os.path.join(directory_path, "refresh_token.txt")

    @staticmethod
    def _read_file(path):
        try:
            with open(path, "r") as _file:
                return _file.read().strip()
        except FileNotFoundError:
            return None

    def get_access_token(self) -> Optional[str]:
        return self._read_file(self._access_token_path)

    def get_refresh_token(self) -> Optional[str]:
        return self._read_file(self._refresh_token_path)

    def save_tokens(self, access_token: str, refresh_token: str):
        with open(self._access_token_path, "w") as _file:
            _file.write(access_token)

        with open(self._refresh_token_path, "w") as _file:
            _file.write(refresh_token)


class RedisTokensStorage(TokensStorage):
    _ACCESS_TOKEN_KEY = "amocrm:access:token"
    _REFRESH_TOKEN_KEY = "amocrm:refresh:token"

    def __init__(self, client, ttl=None):
        self._ttl = ttl
        self._client = client

    def get_access_token(self) -> Optional[str]:
        token = self._client.get(self._ACCESS_TOKEN_KEY)
        if token:
            return token.decode()
        return None

    def get_refresh_token(self) -> Optional[str]:
        token = self._client.get(self._REFRESH_TOKEN_KEY)
        if token:
            return token.decode()
        return None

    def save_tokens(self, access_token: str, refresh_token: str):
        self._client.set(self._ACCESS_TOKEN_KEY, access_token, ex=self._ttl)
        self._client.set(self._REFRESH_TOKEN_KEY, refresh_token, ex=self._ttl)


class TokenManager:
    def __init__(self):
        self._client_id = None
        self._client_secret = None
        self.subdomain = None
        self._redirect_url = None
        self._storage: Optional[TokensStorage] = None

    def __call__(
        self, client_id: str, client_secret: str, subdomain: str, redirect_url: str, storage=FileTokensStorage()
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_url = redirect_url
        if self._storage is None:
            self._storage = storage
        self.subdomain = subdomain

    def init(self, code, skip_error=False):
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self._redirect_url,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        try:
            response = requests.post("https://{}.amocrm.ru/oauth2/access_token".format(self.subdomain), json=data)
        except requests.exceptions.RequestException:
            logger.warning("can't init tokens")
            if not skip_error:
                raise
        else:
            if response.status_code != 200 and not skip_error:
                raise Exception(response.json()["title"])
            if response.status_code != 200 and skip_error:
                return
            response = response.json()
            self._storage.save_tokens(response["access_token"], response["refresh_token"])
            logger.info("successful init and store tokens in %s store", self._storage)

    def _get_new_tokens(self) -> Tuple[str, str]:
        refresh_token = self._storage.get_refresh_token()
        if refresh_token is None:
            raise ValueError()
        body = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "redirect_uri": self._redirect_url,
        }
        response = requests.post("https://{}.amocrm.ru/oauth2/access_token".format(self.subdomain), json=body)
        if response.status_code == 200:
            data = response.json()
            return data["access_token"], data["refresh_token"]
        raise EnvironmentError("Can't refresh token {}".format(response.json()))

    def get_access_token(self):
        token = self._storage.get_access_token()
        if token is None:
            raise exceptions.NoToken("You need to init tokens with code by 'init' method")
        if self._is_expire(token):
            token, refresh_token = self._get_new_tokens()
            self._storage.save_tokens(token, refresh_token)
        return token

    @staticmethod
    def _is_expire(token: str):
        token_data = jwt.decode(token, options={"verify_signature": False})
        exp = datetime.utcfromtimestamp(token_data["exp"])
        now = datetime.utcnow()
        return now >= exp


default_token_manager = TokenManager()
