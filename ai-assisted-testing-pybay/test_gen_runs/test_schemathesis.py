"""Schemathesis contract test using Starlette TestClient + adapter."""

import pytest
import schemathesis
from hypothesis import settings


@pytest.fixture
def web_app(app):
    return schemathesis.openapi.from_asgi("/openapi.json", app)


schema = schemathesis.pytest.from_fixture("web_app")


@settings(deadline=3000)
@schema.parametrize()
def test_openapi_specification(case):
    case.call_and_validate()
