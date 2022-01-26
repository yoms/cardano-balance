from pydantic import BaseModel


class Token(BaseModel):
    """
    Represent a token in cardano blockchain
    """

    fingerprint: str
    name: str
    policy: str
    quantity: int
    price: float = 0
    decimals: float = 0


class Pool(BaseModel):
    """
    Represent an exchange pool
    """

    name: str
    policy: str
    price: float

    @classmethod
    def from_sundae(cls, dict_value) -> 'Pool':
        """
        Compute pool from sundae swap
        """
        data = {}
        data['name'] = dict_value['assetB']['assetName']
        data['policy'] = dict_value['assetB']['assetId'].split('.')[0]
        quantity_a = int(dict_value['quantityA']) / 10 ** int(
            dict_value['assetA']['decimals']
        )
        quantity_b = int(dict_value['quantityB']) / 10 ** int(
            dict_value['assetB']['decimals']
        )
        data['price'] = quantity_a / quantity_b
        return Pool(**data)
