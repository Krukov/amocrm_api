from datetime import datetime, timedelta

import jwt
import pytest

import responses
from amocrm.v2.tokens import TokensStorage, default_token_manager


class FakeStorage(TokensStorage):
    def get_access_token(self):
        token = jwt.encode({"exp": datetime.utcnow() + timedelta(seconds=10)}, "tests")
        if isinstance(token, bytes):
            return token.decode()
        return token


@pytest.fixture(autouse=True)
def _token():
    default_token_manager(client_id="", client_secret="", subdomain="test", redirect_url="", storage=FakeStorage())


@pytest.fixture(name="response_mock")
def _mock():
    with responses.RequestsMock() as _responses:
        yield _responses
