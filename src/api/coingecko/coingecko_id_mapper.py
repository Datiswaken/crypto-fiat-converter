class CoingeckoIdMapper:
    def __init__(self):
        self.id_map = {}

    def get_coingecko_internal_id(self, coin: str) -> str | None:
        return self.id_map.get(coin, None)
