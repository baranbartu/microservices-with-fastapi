from pydantic import BaseModel


class UsernamePasswordForm(BaseModel):
    username: str
    password: str


class UserForm(UsernamePasswordForm):
    email: str = None
    full_name: str = None
    user_type: str


class UserUpdateForm(BaseModel):
    username: str = None
    email: str = None
    full_name: str = None
    user_type: str = None


class OrderForm(BaseModel):
    address: str
    item: str
