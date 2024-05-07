from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any

from requests import Response

from src.api.endpoints import Endpoint


class AbstractApiAdapter(ABC):
    def __init__(self, base_url: str, endpoints: Dict[str, str]) -> None:
        self.base_url = base_url
        self.endpoints = endpoints

    @abstractmethod
    def get_for_date_range(self, start_date: datetime, end_date: datetime, **kwargs) -> dict[str, Any]:
        raise NotImplementedError
