from datetime import datetime
from typing import Dict, Any

from src.api.api_adapter import AbstractApiAdapter
from src.api.coingecko.coingecko_id_mapper import CoingeckoIdMapper
from src.api.endpoints import Endpoint
from src.lib.http_request import build_request, send_request


def _get_ambiguous_coins(coin_list: list[dict], coin_symbol: str) -> list[dict]:
    coins_with_given_symbol = []
    for coin in coin_list:
        if coin["symbol"] == coin_symbol:
            coins_with_given_symbol.append(coin)

    return coins_with_given_symbol


def _resolve_coin_ambiguity(ambiguous_coins: list[dict]):
    print("There is more than 1 coin with the same name available in the Coingecko API.")
    for idx, coin in enumerate(ambiguous_coins):
        platforms = [f"{key} ({value})" for key, value in coin["platforms"].items()]
        print(f"({idx + 1}) Name: {coin['name']}. Available platform(s): {', '.join(platforms)}")
    input_valid = False
    correct_coin_number = 0
    while not input_valid:
        correct_coin_number = int(input("Please choose the number of the correct coin: "))
        if 0 < correct_coin_number <= len(ambiguous_coins):
            input_valid = True
    return ambiguous_coins[correct_coin_number - 1]["id"]


class CoingeckoApiAdapter(AbstractApiAdapter):
    def __init__(self, id_mapper: CoingeckoIdMapper, base_url: str, endpoints: Dict[str, str]):
        super().__init__(base_url, endpoints)
        self.id_mapper = id_mapper

    def _load_coins(self, coin_symbol: str) -> dict[str, str]:
        endpoint = self.endpoints[Endpoint.COINS.value]
        url = self.base_url + endpoint
        request = build_request(url, method="GET")
        response = send_request(request=request).json()

        if "status" in response and "error_code" in response["status"]:
            if response["status"]["error_code"] == 429:
                print(f"You have exceeded the rate limit of Coingecko. Please wait some time and try again")

        coin_mapping = {coin["symbol"]: coin["id"] for coin in response}
        ambiguous_coins = _get_ambiguous_coins(coin_list=response, coin_symbol=coin_symbol)
        if len(ambiguous_coins) > 1:
            correct_coin = _resolve_coin_ambiguity(ambiguous_coins=ambiguous_coins)
            coin_mapping[coin_symbol] = correct_coin

        return coin_mapping

    def _get_coingecko_id(self, coin: str):
        return self.id_mapper.get_coingecko_internal_id(coin=coin)

    def get_for_date_range(self, start_date: datetime, end_date: datetime, **kwargs) -> dict[str, Any]:
        if not self.id_mapper.id_map:
            self.id_mapper.id_map.update(self._load_coins(kwargs["convert_from"].lower()))
        convert_from = self._get_coingecko_id(coin=kwargs["convert_from"].lower())
        convert_to = kwargs["convert_to"].lower()

        endpoint = self.endpoints[Endpoint.DATE_RANGE.name]
        endpoint = (endpoint
                    .replace("{convert_from}", convert_from)
                    .replace("{from}", str(start_date.timestamp()))
                    .replace("{to}", str(end_date.timestamp()))
                    .replace("{convert_to}", convert_to)
                    )
        url = self.base_url + endpoint
        request = build_request(url=url, method="GET")

        return send_request(request=request).json()
