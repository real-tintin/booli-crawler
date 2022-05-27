from dataclasses import dataclass
from http import HTTPStatus


@dataclass
class MockResponse:
    content: bytes
    status_code: int = HTTPStatus.OK
