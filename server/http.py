from socket import socket
from enum import Enum
from typing import Callable
from .logger import logger

class Methods(Enum):
    GET = "GET"
    POST = "POST"

Route = list[Callable[[socket, str, bytes], bool]]

def decode_data(data: bytes):
    return data.decode("utf-8")

def encode_message(message):
    return str(message).encode('utf-8')

def HttpRoute(method: Methods = Methods.GET, route: str = None):
    comp = method.value + ' '
    if route:
        comp += f'{route} '

    def decorator(func):
        def wrapper(*args, **kwargs):
            if kwargs['message'].startswith(comp):
                logger(kwargs['conn'], 'Requisição', comp)
                func(*args, **kwargs)
                return True
            return False
        return wrapper
    return decorator
