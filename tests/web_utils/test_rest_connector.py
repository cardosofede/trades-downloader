import asyncio
import json
import unittest
from typing import Awaitable
from urllib.parse import urljoin

import aiohttp

from trades_downloader.web_utils.data_types import RESTMethod
from trades_downloader.web_utils.rest_connector import RESTConnector


class RestConnectorTests(unittest.TestCase):
    level = 0

    @classmethod
    def setUpClass(cls) -> None:
        cls.ev_loop = asyncio.get_event_loop()
        cls._session = aiohttp.ClientSession()

    def setUp(self) -> None:
        self.log_records = []
        self._public_url = "https://api.binance.com"
        self._public_connector = RESTConnector(base_public_url=self._public_url, session=self._session,
                                               timeout=1.0)
        self._public_connector.logger().setLevel(1)
        self._public_connector.logger().addHandler(self)

    def async_run_with_timeout(self, coroutine: Awaitable, timeout: int = 5):
        ret = self.ev_loop.run_until_complete(asyncio.wait_for(coroutine, timeout))
        return ret

    @property
    def public_url_response(self):
        return {
            "symbol": "LUPIN-USDT",
            "priceChange": "-94.99999800",
            "priceChangePercent": "-95.960",
            "weightedAvgPrice": "0.29628482",
            "prevClosePrice": "0.10002000",
            "lastPrice": "4.00000200",
            "lastQty": "200.00000000",
            "bidPrice": "4.00000000",
            "bidQty": "100.00000000",
            "askPrice": "4.00000200",
            "askQty": "100.00000000",
            "openPrice": "99.00000000",
            "highPrice": "100.00000000",
            "lowPrice": "0.10000000",
            "volume": "8913.30000000",
            "quoteVolume": "15.30000000",
            "openTime": 1499783499040,
            "closeTime": 1499869899040,
            "firstId": 28385,  # First tradeId
            "lastId": 28460,  # Last tradeId
            "count": 76  # Trade count
        }

    @aioresponses()
    async def test_api_request(self, mock_api):
        response = self.public_url_response
        endpoint = "/api/v3/ticker/24hr"
        url = urljoin(self._public_url, endpoint)

        mock_api.get(url, body=json.dumps(response))
        request = await self._public_connector.api_request(endpoint=endpoint,
                                                           rest_method=RESTMethod.GET)
        json_response = await request.json()
        self.assertEqual(url, request.url)
        self.assertEqual("LUPIN-USDT", json_response["symbol"])
