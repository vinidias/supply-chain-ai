"""Pydantic models para a API."""
from datetime import datetime

from pydantic import BaseModel, Field


class Supplier(BaseModel):
    id: int
    name: str
    country: str
    category: str
    rating: float


class Product(BaseModel):
    id: int
    name: str
    category: str
    supplier_id: int
    unit_cost: float
    lead_time_days: int


class Order(BaseModel):
    id: int
    product_id: int
    order_date: datetime
    quantity: int
    unit_price: float
    status: str


class AskRequest(BaseModel):
    question: str = Field(..., description="Pergunta em linguagem natural sobre supply chain")


class AskResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    model: str
