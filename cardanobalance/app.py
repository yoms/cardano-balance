import sys

import click
from tabulate import tabulate

from cardanobalance import compute_balance, get_ada_price


@click.command()
@click.option(
    "-s",
    "--stacking-key",
    "stacking_key",
    required=True,
    help="Stacking key",
)
@click.option(
    "-c",
    "--currency",
    "currency",
    required=False,
    help="Currency displayed",
    default='ada',
)
def main(
    stacking_key: str,
    currency: str,
) -> None:
    """Main function"""
    ada_price = get_ada_price()
    if currency not in ada_price:
        print(
            f'Currency {currency} not found, '
            f'should be one of {", ".join(list(ada_price.keys()))}'
        )
        sys.exit(1)
    balance = compute_balance(stacking_key)
    tables_data = []
    for asset in balance:
        quantity = asset.quantity / 10 ** asset.decimals
        price = asset.price * ada_price[currency]
        balance = price * quantity
        tables_data.append([asset.name, quantity, price, balance])

    tables = [
        ['Token name', 'quantity', f'token price ({currency})', f'balance ({currency})']
    ]
    tables_data.sort(key=lambda value: value[-1], reverse=True)
    tables.extend(tables_data)
    print(tabulate(tables, headers=("firstrow"), floatfmt="0.16f"))
