from pydantic import BaseModel

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Orders(models.Model):
    id = fields.IntField(pk=True)
    address = fields.TextField()
    item = fields.TextField()
    created_by = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)


Order_Pydantic = pydantic_model_creator(Orders, name='Order')


class OrderIn_Pydantic(BaseModel):
    address: str
    item: str
