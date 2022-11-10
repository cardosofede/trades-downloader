import asyncio
import json
from urllib.parse import urljoin

import aiohttp
import pytest
from aioresponses import aioresponses

from trades_downloader.web_utils.data_types import RESTMethod
from trades_downloader.web_utils.rest_connector import RESTConnector


@pytest.fixture(scope="class")
def ev_loop():
    return asyncio.get_event_loop()


@pytest.fixture
def mock_api():
    with aioresponses() as m:
        yield m


@pytest.fixture(scope="class")
def session():
    session = aiohttp.ClientSession()
    yield session
    session.close()


@pytest.fixture(scope="class")
def public_rest_connector(session):
    return RESTConnector(
        base_public_url="https://api.binance.com", session=session, timeout=1.0
    )


class TestRestConnector:
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
            "count": 76,  # Trade count
        }

    @pytest.mark.asyncio
    async def test_api_request(self, public_rest_connector, ev_loop, mock_api):
        response = self.public_url_response
        endpoint = "/api/v3/ticker/24hr"
        base_url = "https://api.binance.com"
        url = urljoin(base_url, endpoint)

        mock_api.get(url, body=json.dumps(response))
        request = await public_rest_connector.api_request(
            endpoint=endpoint, rest_method=RESTMethod.GET
        )
        json_response = await request.json()
        assert url == request.url
        assert "LUPIN-USDT" == json_response["symbol"]
