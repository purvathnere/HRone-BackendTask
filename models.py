from pydantic import BaseModel
from typing import List

class Size(BaseModel):
    size: str
    quantity: int

class Product(BaseModel):
    name: str
    price: float
    sizes: List[Size]

class OrderThing(BaseModel):
    product_id: str
    quantity: int

class OrderDetail(BaseModel):
    user_id: str
    items: List[OrderThing]
