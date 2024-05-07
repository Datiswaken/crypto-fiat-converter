import yaml

from dependency_injector import containers, providers

from src.api.coingecko.coingecko_api_adapter import CoingeckoApiAdapter
from src.api.coingecko.coingecko_id_mapper import CoingeckoIdMapper


class Container(containers.DeclarativeContainer):
    config_file_path = f"./config/api.yaml"
    with open(config_file_path, "r") as config_file:
        configs = yaml.safe_load(config_file)

    coingecko_id_mapper = providers.Factory(CoingeckoIdMapper)

    cg_base_url = configs["coingecko"]["base_url"]
    cg_endpoints = configs["coingecko"]["endpoints"]
    coingecko_api_adapter = providers.Factory(
        CoingeckoApiAdapter,
        id_mapper=coingecko_id_mapper,
        base_url=cg_base_url,
        endpoints=cg_endpoints
    )
