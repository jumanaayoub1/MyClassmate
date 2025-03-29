import bcrypt
import jwt
import datetime
import os
from fastapi import Request, HTTPException


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

def validate_user_cookie(request: Request):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")

    token = auth_header.split(" ")[1]

    try:
        secret_key = os.environ.get("JWT_KEY", "testing_key")
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return {"user_id": payload["user_id"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
