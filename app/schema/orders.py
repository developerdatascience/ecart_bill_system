from typing import List
from pydantic import BaseModel


class IngredientListBase(BaseModel):
    """Represents a list of ingredients"""
    name: str
    product_id: int
    quantity: float

class BillBase(BaseModel):
    """Repesent ingredient in a recipe"""
    bill_no: int
    bill_date: str
    ingredients: List[IngredientListBase]

class BillResponse(BillBase):
    """Response model for a bill"""
    ingredients: List[IngredientListBase]

class ShopListBase(BaseModel):
    """Request model needs bill number and ingredients"""
    ingredient_list: List[IngredientListBase]
