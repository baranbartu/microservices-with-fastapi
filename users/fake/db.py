import json

from datastructures import UserInDb, UserUpdateForm


users_file = 'fake/users.json'


def get_all_users(db: str = users_file):
    with open(db) as json_file:
        users = json.load(json_file)
        for user in users:
            yield UserInDb(**user)


def get_user_by_id(uid: int):
    users = list(filter(lambda u: u.id == uid, get_all_users()))
    return users[0] if users else None


def get_user_by_username(uname: str):
    users = list(filter(lambda u: u.username == uname, get_all_users()))
    return users[0] if users else None


def get_user_by_email(email: str):
    users = list(filter(lambda u: u.email == email, get_all_users()))
    return users[0] if users else None


def insert_user(data: dict, hashed_password: str, created_by: int):
    try:
        last_id = max(map(lambda u: u.id, get_all_users()))
        pk = last_id + 1
    except ValueError:
        pk = 1

    data.update({
        'id': pk,
        'hashed_password': hashed_password,
        'created_by': created_by
    })

    user_in_db = UserInDb(**data)
    users = list(map(lambda u: u.dict(), get_all_users()))
    users.append(user_in_db.dict())

    dump_users(users)

    return user_in_db


def delete_user_from_db(pk: int):
    users = list(
        map(
            lambda u: u.dict(),
            filter(lambda u: u.id != pk, get_all_users())
        )
    )
    dump_users(users)


def update_user_in_db(user_in_db: UserInDb, user: UserUpdateForm):
    new_user_data = user.dict()
    db_user_data = user_in_db.dict()
    for column, value in new_user_data.items():
        if value is not None:
            db_user_data[column] = value

    new_db_users = list(
        map(
            lambda u: u.dict() if u.id != user_in_db.id else db_user_data,
            get_all_users()
        )
    )
    dump_users(new_db_users)

    user_in_db = UserInDb(**db_user_data)
    return user_in_db


def dump_users(users: list, db: str = users_file):
    with open(db, 'w') as json_file:
        json.dump(users, json_file, indent=4)
