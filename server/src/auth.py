import bcrypt
import jwt
import datetime
import os
from fastapi import Request, HTTPException, Cookie, status

import logging
logger = logging.getLogger(__name__)


def hash_password(plaintext_password: str) -> tuple[str, str]:
    """
    We need to hash passwords before storing them in our database
    Params
     * plaintext_password: password to encrypt
    Returns
     * (salt: str, hashed_pw: str)
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plaintext_password.encode(), salt)

    return salt.decode(), hashed_password.decode()

def login_user(plaintext_password: str, stored_salt: str, stored_hash: str) -> bool:
    """
    verify if our password matches the stored password
    Params
     * plaintext_password: user input
     * stored_salt: salt for user (from db)
     * stored hash: hashed password (from db)
    Returns
     * valid_login: bool
    """
    hashed_attempt = bcrypt.hashpw(plaintext_password.encode(), stored_salt.encode())
    return hashed_attempt.decode() == stored_hash

def generate_jwt(user_id: int):
    secret_key = os.environ.get("JWT_KEY", "testing_key")
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Expires in 1 hour
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

def validate_user_cookie(access_token: str = Cookie(None)): 
    logger.info(f"COOKIE: {access_token}")
    if not access_token:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        secret_key = os.environ.get("JWT_KEY", "testing_key")
        payload = jwt.decode(access_token, secret_key, algorithms=["HS256"])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid")
