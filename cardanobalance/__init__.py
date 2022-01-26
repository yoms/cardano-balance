from typing import List
import requests

from cardanobalance.model import Token, Pool


def sundae_assets_prices() -> List[Pool]:
    api_url = 'https://stats.sundaeswap.finance/graphql'
    request_data = {"query": "query getPoolsByAssetIds($assetIds: [String!]!) {\n  pools(assetIds: $assetIds) {\n    ...PoolFragment\n  }\n}\n\nfragment PoolFragment on Pool {\n  assetA {\n    ...AssetFragment\n  }\n  assetB {\n    ...AssetFragment\n  }\n  assetLP {\n    ...AssetFragment\n  }\n  fee\n  quantityA\n  quantityB\n  quantityLP\n  ident\n  assetID\n}\n\nfragment AssetFragment on Asset {\n  assetId\n  policyId\n  assetName\n  decimals\n ticker\n  dateListed\n}\n",
                    "variables": {"assetIds": [""]},
                    "operationName": "getPoolsByAssetIds"}
    data = requests.post(api_url, json=request_data)
    raw_data = data.json()
    pools = raw_data['data']['pools']

    return [Pool.from_sundae(p) for p in pools]


def list_assets(staking_key: str) -> List[Token]:
    data = requests.get(f'https://pool.pm/wallet/{staking_key}')
    wallet = data.json()

    tokens = [Token(**t) for t in wallet['tokens']]
    # Add ADA
    tokens.append(Token(
        fingerprint='',
        minted=0,
        minted_quantity=0,
        name='ada',
        policy="",
        quantity=wallet['lovelaces'] + wallet['reward'],
        price=1,
        decimals=6))

    return tokens


def compute_balance(staking_key: str):
    assets = list_assets(staking_key)
    pools = sundae_assets_prices()
    pools_map = {f'{p.name}_{p.policy}': p for p in pools}

    for a in assets:
        key_value = f'{a.name}_{a.policy}'
        if key_value in pools_map:
            a.price = pools_map[key_value].price
    return assets


def get_ada_price() -> dict:
    data = requests.get('https://pool.pm/total.json')
    ada_prices = data.json()
    filtered_prices = {'ada' : 1}
    for key, value in ada_prices.items():
        if key[:3] == 'ADA'  :
            filtered_prices[key[3:].lower()] = value

    return filtered_prices