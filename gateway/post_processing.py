from auth import generate_access_token


def access_token_generate_handler(data):
    access_token = generate_access_token(data)
    return {
        'access_token': access_token, 'token_type': 'bearer'
    }
