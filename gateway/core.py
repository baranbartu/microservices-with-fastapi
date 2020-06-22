import aiohttp
import functools


from importlib import import_module
from fastapi import Request, Response, HTTPException, status
from typing import List

from exceptions import (AuthTokenMissing, AuthTokenExpired, AuthTokenCorrupted)
from network import make_request


def route(
        request_method, path: str, status_code: int,
        payload_key: str, service_url: str,
        authentication_required: bool = False,
        post_processing_func: str = None,
        authentication_token_decoder: str = 'auth.decode_access_token',
        service_authorization_checker: str = 'auth.is_admin_user',
        service_header_generator: str = 'auth.generate_request_header',
        response_model: str = None,
        response_list: bool = False
):
    """
    it is an advanced wrapper for FastAPI router, purpose is to make FastAPI
    acts as a gateway API in front of anything

    Args:
        request_method: is a callable like (app.get, app.post and so on.)
        path: is the path to bind (like app.post('/api/users/'))
        status_code: expected HTTP(status.HTTP_200_OK) status code
        payload_key: used to easily fetch payload data in request body
        authentication_required: is bool to give to user an auth priviliges
        post_processing_func: does extra things once in-network service returns
        authentication_token_decoder: decodes JWT token as a proper payload
        service_authorization_checker: does simple front authorization checks
        service_header_generator: generates headers for inner services from jwt token payload # noqa
        response_model: shows return type and details on api docs
        response_list: decides whether response structure is list or not

    Returns:
        wrapped endpoint result as is

    """

    # request_method: app.post || app.get or so on
    # app_any: app.post('/api/login', status_code=200, response_model=int)
    if response_model:
        response_model = import_function(response_model)
        if response_list:
            response_model = List[response_model]

    app_any = request_method(
        path, status_code=status_code,
        response_model=response_model
    )

    def wrapper(f):
        @app_any
        @functools.wraps(f)
        async def inner(request: Request, response: Response, **kwargs):
            service_headers = {}

            if authentication_required:
                # authentication
                authorization = request.headers.get('authorization')
                token_decoder = import_function(authentication_token_decoder)
                exc = None
                try:
                    token_payload = token_decoder(authorization)
                except (AuthTokenMissing,
                        AuthTokenExpired,
                        AuthTokenCorrupted) as e:
                    exc = str(e)
                except Exception as e:
                    # in case a new decoder is used by dependency injection and
                    # there might be an unexpected error
                    exc = str(e)
                finally:
                    if exc:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=exc,
                            headers={'WWW-Authenticate': 'Bearer'},
                        )

                # authorization
                if service_authorization_checker:
                    authorization_checker = import_function(
                        service_authorization_checker
                    )
                    is_user_eligible = authorization_checker(token_payload)
                    if not is_user_eligible:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail='You are not allowed to access this scope.',
                            headers={'WWW-Authenticate': 'Bearer'},
                        )

                # service headers
                if service_header_generator:
                    header_generator = import_function(
                        service_header_generator
                    )
                    service_headers = header_generator(token_payload)

            scope = request.scope

            method = scope['method'].lower()
            path = scope['path']

            payload_obj = kwargs.get(payload_key)
            payload = payload_obj.dict() if payload_obj else {}

            url = f'{service_url}{path}'

            try:
                resp_data, status_code_from_service = await make_request(
                    url=url,
                    method=method,
                    data=payload,
                    headers=service_headers,
                )
            except aiohttp.client_exceptions.ClientConnectorError:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail='Service is unavailable.',
                    headers={'WWW-Authenticate': 'Bearer'},
                )
            except aiohttp.client_exceptions.ContentTypeError:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail='Service error.',
                    headers={'WWW-Authenticate': 'Bearer'},
                )

            response.status_code = status_code_from_service

            if all([
                status_code_from_service == status_code,
                post_processing_func
            ]):
                post_processing_f = import_function(post_processing_func)
                resp_data = post_processing_f(resp_data)

            return resp_data

    return wrapper


def import_function(method_path):
    module, method = method_path.rsplit('.', 1)
    mod = import_module(module)
    return getattr(mod, method, lambda *args, **kwargs: None)
