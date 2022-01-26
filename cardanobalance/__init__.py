from typing import List

import requests

from cardanobalance.model import Pool, Token


def _sundae_assets_prices() -> List[Pool]:
    """
    Return the prices of each token in sundaeswap
    """
    api_url = 'https://stats.sundaeswap.finance/graphql'
    request_data = {
        "query": "query getPoolsByAssetIds($assetIds: [String!]!) {\n"
        "  pools(assetIds: $assetIds) {\n"
        "    ...PoolFragment\n"
        "  }\n"
        "}\n"
        "\n"
        "fragment PoolFragment on Pool {\n"
        "  assetA {\n"
        "    ...AssetFragment\n"
        "  }\n"
        "  assetB {\n"
        "    ...AssetFragment\n"
        "  }\n"
        "  assetLP {\n"
        "    ...AssetFragment\n"
        "  }\n"
        "  fee\n"
        "  quantityA\n"
        "  quantityB\n"
        "  quantityLP\n"
        "  ident\n"
        "  assetID\n"
        "}\n"
        "\n"
        "fragment AssetFragment on Asset {\n"
        "  assetId\n"
        "  policyId\n"
        "  assetName\n"
        "  decimals\n"
        " ticker\n"
        "  dateListed\n"
        "}\n",
        "variables": {"assetIds": [""]},
        "operationName": "getPoolsByAssetIds",
    }
    data = requests.post(api_url, json=request_data)
    raw_data = data.json()
    pools = raw_data['data']['pools']

    return [Pool.from_sundae(p) for p in pools]


def _list_assets(staking_key: str) -> List[Token]:
    """
    Return the list of Token in the wallet corresponding to
    the stacking key
    """
    data = requests.get(f'https://pool.pm/wallet/{staking_key}')
    wallet = data.json()

    tokens = [Token(**t) for t in wallet['tokens']]
    # Add ADA
    tokens.append(
        Token(
            fingerprint='',
            minted=0,
            minted_quantity=0,
            name='ada',
            policy="",
            quantity=wallet['lovelaces'] + wallet['reward'],
            price=1,
            decimals=6,
        )
    )

    return tokens


def compute_balance(staking_key: str) -> List[Token]:
    """
    Return the list of Token in the wallet corresponding to
    the stacking key with their prices if found
    """
    assets = _list_assets(staking_key)
    pools = _sundae_assets_prices()
    pools_map = {f'{p.name}_{p.policy}': p for p in pools}

    for asset in assets:
        key_value = f'{asset.name}_{asset.policy}'
        if key_value in pools_map:
            asset.price = pools_map[key_value].price
    return assets


def get_ada_price() -> dict:
    """
    Return the ada prices in several fiat currency
    """
    data = requests.get('https://pool.pm/total.json')
    ada_prices = data.json()
    filtered_prices = {'ada': 1}
    for key, value in ada_prices.items():
        if key[:3] == 'ADA':
            filtered_prices[key[3:].lower()] = value

    return filtered_prices
