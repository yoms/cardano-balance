from pydantic import BaseModel


class Token(BaseModel):
    fingerprint: str
    minted: int
    minted_quantity: int
    name: str
    policy: str
    quantity: int
    price: float = 0
    decimals: float = 0


class Pool(BaseModel):
    name: str
    policy: str
    price: float

    @classmethod
    def from_sundae(cls, dict_value) -> 'Pool':
        data = {}
        data['name'] = dict_value['assetB']['assetName']
        data['policy'] = dict_value['assetB']['assetId'].split('.')[0]
        quantityA = int(dict_value['quantityA'])/10**int(dict_value['assetA']['decimals'])
        quantityB = int(dict_value['quantityB'])/10**int(dict_value['assetB']['decimals'])
        data['price'] = quantityA / quantityB
        return Pool(**data)
