from fastapi import FastAPI, HTTPException, status, Request, Response, Header

from auth import verify_password, get_password_hash
from datastructures import UsernamePasswordForm, UserForm, UserUpdateForm

from fake.db import (get_user_by_username,
                     get_user_by_email,
                     insert_user,
                     get_all_users,
                     get_user_by_id,
                     delete_user_from_db,
                     update_user_in_db)

app = FastAPI()
PROTECTED_USER_IDS = [1, 2]


@app.post('/api/login', status_code=status.HTTP_201_CREATED)
async def login(form_data: UsernamePasswordForm):
    user_in_db = get_user_by_username(form_data.username)

    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found with this username.',
        )

    verified = verify_password(form_data.password, user_in_db.hashed_password)
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Password is wrong.',
        )

    return user_in_db


@app.post('/api/users', status_code=status.HTTP_201_CREATED)
async def create_user(user: UserForm,
                      request: Request, response: Response,
                      request_user_id: str = Header(None)):

    user_in_db = get_user_by_username(user.username)
    if user_in_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='There is already another user with this username.',
        )

    user_in_db = get_user_by_email(user.email)
    if user_in_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='There is already another user with this email.',
        )

    hashed_password = get_password_hash(user.password)
    data = user.dict()
    user_in_db = insert_user(data, hashed_password, request_user_id)

    return user_in_db


@app.get('/api/users', status_code=status.HTTP_200_OK)
async def get_users(request: Request, response: Response,
                    request_user_id: str = Header(None)):
    users = list(get_all_users())
    return users


@app.get('/api/users/{user_id}', status_code=status.HTTP_200_OK)
async def get_user(user_id: int, request: Request, response: Response,
                   request_user_id: str = Header(None)):

    user_in_db = get_user_by_id(user_id)
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found with this id.',
        )
    return user_in_db


@app.delete('/api/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, request: Request, response: Response,
                      request_user_id: str = Header(None)):

    if user_id in PROTECTED_USER_IDS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not allowed to delete protected users.',
        )

    user_in_db = get_user_by_id(user_id)
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found with this id.',
        )
    delete_user_from_db(user_id)


@app.put('/api/users/{user_id}', status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user: UserUpdateForm,
                      request: Request, response: Response,
                      request_user_id: str = Header(None)):

    user_in_db = get_user_by_id(user_id)
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='There is already another user with this username.',
        )

    user_in_db = update_user_in_db(user_in_db, user)
    return user_in_db
