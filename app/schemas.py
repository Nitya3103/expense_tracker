from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class Category(str, Enum):
    food = "food"
    transport = "transport"
    rent = "rent"
    shopping = "shopping"
    bills = "bills"
    other = "other"


class ExpenseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category: Category = Category.other
    spent_on: date


class ExpenseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    amount: Decimal | None = Field(default=None, gt=0)
    category: Category | None = None
    spent_on: date | None = None


class ExpenseOut(BaseModel):
    id: int
    title: str
    amount: Decimal
    category: Category
    spent_on: date

    model_config = {"from_attributes": True}
