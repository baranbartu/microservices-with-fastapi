from pydantic import BaseModel


class OrderForm(BaseModel):
    address: str
    item: str


class OrderResponse(BaseModel):
    id: int
    address: str
    item: str
    created_by: int
    created_at: str
