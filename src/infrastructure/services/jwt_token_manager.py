import os
from typing import Self

import jwt
from datetime import datetime, timedelta

from src.application.contracts import TokenManager
from src.shared.result import Result


class JWTTokenManager(TokenManager):
    def __init__(self: Self) -> None:
        self._secret = os.environ.get('JWT_SECRET', 'default-secret')
        self._algorithm = os.environ.get('JWT_ALGORITHM', 'HS256')
        self._expiration_hours = int(os.environ.get('JWT_EXPIRATION_HOURS', '24'))

    def create(self: Self, payload: dict) -> str:
        to_encode = payload.copy()
        expire = datetime.utcnow() + timedelta(hours=self._expiration_hours)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self._secret, algorithm=self._algorithm)

    def verify(self: Self, token: str) -> Result[dict, Exception]:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            return Result.ok(payload)
        except jwt.ExpiredSignatureError:
            return Result.fail([Exception("Token has expired")])
        except jwt.InvalidTokenError:
            return Result.fail([Exception("Invalid token")])
