import asyncio
import json
import logging
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import aiohttp

from trades_downloader.web_utils.auth import AuthBase
from trades_downloader.web_utils.data_types import (
    RESTMethod,
    RESTRequest,
    RESTResponse,
    UnauthorizedError,
)


class RESTConnector:
    _logger = None

    def __init__(
        self,
        base_public_url: Optional[str] = None,
        base_private_url: Optional[str] = None,
        auth: Optional[AuthBase] = None,
        session: Optional[aiohttp.ClientSession] = None,
        timeout: Optional[float] = 3,
        max_retries: Optional[int] = 3,
        # TODO: Implement throttler
    ) -> object:
        self._base_public_url = base_public_url
        self._base_private_url = base_private_url
        self._auth = auth
        self._session = session
        self._timeout = timeout
        self._max_retries = max_retries

    @classmethod
    async def get_connection(
        cls,
        base_public_url: Optional[str] = None,
        base_private_url: Optional[str] = None,
        session: Optional[aiohttp.ClientSession] = None,
        timeout: Optional[float] = 3,
        max_retries: Optional[int] = 3,
    ):
        session = session or aiohttp.ClientSession()
        return RESTConnector(
            base_public_url=base_public_url,
            base_private_url=base_private_url,
            session=session,
            timeout=timeout,
            max_retries=max_retries,
        )

    @classmethod
    def logger(cls):
        if cls._logger is None:
            cls._logger = logging.getLogger(__name__)
        return cls._logger

    @staticmethod
    async def _build_resp(aiohttp_resp: aiohttp.ClientResponse) -> RESTResponse:
        resp = RESTResponse(aiohttp_resp)
        return resp

    async def _execute_request(
        self, rest_request: RESTRequest
    ) -> Union[str, Dict[str, Any]]:
        response: aiohttp.ClientResponse = await self._session.request(
            method=rest_request.rest_method,
            url=urljoin(rest_request.url, rest_request.endpoint),
            params=rest_request.params,
            data=rest_request.data,
            headers=rest_request.headers,
        )
        response.raise_for_status()
        result = await self._build_resp(response)
        return result

    async def api_request(
        self,
        url: Optional[str] = None,
        endpoint: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        rest_method: RESTMethod = RESTMethod.GET,
        is_auth_required: bool = False,
    ) -> Union[Exception, RESTResponse]:
        last_exception = None
        if is_auth_required:
            url = url or self._base_private_url
        else:
            url = url or self._base_public_url
        if not url:
            raise UnauthorizedError

        headers = headers or {}
        params = params or {}

        local_headers = {
            "Content-Type": (
                "application/json"
                if rest_method in [RESTMethod.POST, RESTMethod.PUT]
                else "application/x-www-form-urlencoded"
            )
        }
        local_headers.update(headers)

        data = json.dumps(data) if data is not None else data

        rest_request = RESTRequest(
            rest_method=rest_method,
            url=url,
            endpoint=endpoint or "",
            params=params,
            headers=local_headers,
            data=data,
        )
        # TODO: Improve try catch to log and return the errors not related with the request.
        if is_auth_required:
            if not self._auth:
                raise UnauthorizedError
            else:
                self._auth.rest_authenticate(rest_request)

        for _ in range(self._max_retries):
            try:
                request_result = await asyncio.wait_for(
                    self._execute_request(rest_request=rest_request),
                    timeout=self._timeout,
                )
                return request_result
            except Exception as request_exception:
                last_exception = request_exception
                self.logger().exception(
                    f"Retrying in 5 seconds... Exception: {last_exception}"
                )
                await asyncio.sleep(5)
        return last_exception
