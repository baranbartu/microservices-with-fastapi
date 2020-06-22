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


class UserInDb(BaseModel):
    id: int
    username: str
    email: str = None
    full_name: str = None
    user_type: str
    hashed_password: str
    created_by: int
