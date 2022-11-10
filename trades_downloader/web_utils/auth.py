from abc import ABC, abstractmethod

from trades_downloader.web_utils.data_types import RESTRequest


class AuthBase(ABC):
    @abstractmethod
    def rest_authenticate(self, request: RESTRequest):
        ...
