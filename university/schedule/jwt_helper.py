import jwt
from datetime import datetime, timezone
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

KEY = settings.JWT["SIGNING_KEY"]
ALGORITHM = settings.JWT["ALGORITHM"]
ACCESS_TOKEN_LIFETIME = settings.JWT["ACCESS_TOKEN_LIFETIME"]
REFRESH_TOKEN_LIFETIME = settings.JWT["REFRESH_TOKEN_LIFETIME"]


def create_access_token(user_id):
    # Create initial payload
    payload = {
        "token_type": "access",
        "exp": datetime.now(tz=timezone.utc) + ACCESS_TOKEN_LIFETIME,
        "iat": datetime.now(tz=timezone.utc),
    }
    # Add given arguments to payload
    payload["user_id"] = user_id
    # Create Token
    token = jwt.encode(payload, KEY, algorithm=ALGORITHM)
    return token


def create_refresh_token(user_id):
    # Create initial payload
    payload = {
        "token_type": "refresh",
        "exp": datetime.now(tz=timezone.utc) + REFRESH_TOKEN_LIFETIME,
        "iat": datetime.now(tz=timezone.utc),
    }
    # Add given arguments to payload
    payload["user_id"] = user_id
    # Create token
    token = jwt.encode(payload, KEY, ALGORITHM)
    return token


def get_jwt_payload(token):
    payload = jwt.decode(token, KEY, algorithms=[ALGORITHM])
    return payload


def get_access_token(request):
    token = request.COOKIES.get('access_token')

    if token is None:
        token = request.data.get('access_token')

    if token is None:
        token = request.headers.get("authorization")

    return token


def get_refresh_token(request):
    token = request.COOKIES.get('refresh_token')

    if token is None:
        token = request.data.get('refresh_token')

    return token
