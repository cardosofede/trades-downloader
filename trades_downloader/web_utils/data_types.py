from dataclasses import dataclass
from enum import Enum
from typing import Optional, Mapping, Any

import aiohttp


class RESTMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"

    def __str__(self):
        obj_str = repr(self)
        return obj_str

    def __repr__(self):
        return self.value


@dataclass
class RESTRequest:
    rest_method: RESTMethod
    url: Optional[str] = None
    endpoint: Optional[str] = None
    params: Optional[Mapping[str, str]] = None
    data: Any = None
    headers: Optional[Mapping[str, str]] = None
    throttler_limit_id: Optional[str] = None


@dataclass(init=False)
class RESTResponse:
    url: str
    method: RESTMethod
    status: int
    headers: Optional[Mapping[str, str]]

    def __init__(self, aiohttp_response: aiohttp.ClientResponse):
        self._aiohttp_response = aiohttp_response

    @property
    def url(self) -> str:
        url_str = str(self._aiohttp_response.url)
        return url_str

    @property
    def method(self) -> RESTMethod:
        method_ = RESTMethod[self._aiohttp_response.method.upper()]
        return method_

    @property
    def status(self) -> int:
        status_ = int(self._aiohttp_response.status)
        return status_

    @property
    def headers(self) -> Optional[Mapping[str, str]]:
        headers_ = self._aiohttp_response.headers
        return headers_

    async def json(self) -> Any:
        json_ = await self._aiohttp_response.json()
        return json_

    async def text(self) -> str:
        text_ = await self._aiohttp_response.text()
        return text_


class UrlNotDefinedError(Exception):
    """
    Error raised if a request without url is trying to get executed.
    This can be either if is not present the url of the api request
    and the base_url of the rest connector.
    """

    def __str__(self) -> str:
        return "Cannot send request because the url is missing."


class UnauthorizedError(Exception):
    """
    Error raised if a request without url is trying to get executed.
    This can be either if is not present the url of the api request
    and the base_url of the rest connector.
    """

    def __str__(self) -> str:
        return "Cannot send request because needs auth and the Auth Module is None."
