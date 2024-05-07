from datetime import date, datetime
from typing import Any

from src.api.api_adapter import AbstractApiAdapter
from src.fiat_currencies import FiatCurrency


def convert_for_date_range(
    api_adapter: AbstractApiAdapter,
    start_date: datetime,
    end_date: datetime,
    convert_from: str,
    convert_to: FiatCurrency = FiatCurrency.USD
) -> dict[str, Any]:
    return api_adapter.get_for_date_range(
        start_date=start_date,
        end_date=end_date,
        convert_from=convert_from,
        convert_to=convert_to
    )




