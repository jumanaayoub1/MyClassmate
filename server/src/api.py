from fastapi import APIRouter, Depends, status, Response
import sqlite3
from pydantic import BaseModel

import db
import auth

import logging
logger = logging.getLogger(__name__)

user_router = APIRouter(prefix="/user", tags=["user"])

class RegisterUser(BaseModel):
    id: int
    username: str | None
    password: str
    privacy: str | None
    major: str | None

@user_router.post("/register")
def register_user(user: RegisterUser, response: Response, con: sqlite3.Connection = Depends(db.get_db)):
    logger.info(f"attempting to register user: {user.id}")
    try:
        db.insert_user(
                con,
                user.id,
                user.password,
                username=user.username,
                privacy=user.privacy,
                major=user.major
                )
        logger.info(f"registered user: {user.id}")
        response.status_code = status.HTTP_201_CREATED
    except Exception as e:
        logger.info(f"failed to register user: {user.id}, error: {e}")
        response.status_code = status.HTTP_409_CONFLICT

class LoginUser(BaseModel):
    id: int
    password: str

@user_router.post("/login")
def login(user: LoginUser, response: Response, con: sqlite3.Connection = Depends(db.get_db)):
    logger.info(f"attempting to login for user_id: {user.id}")
    try:
        info = db.get_login_info(con, user.id)
        if auth.login_user(user.password, info["salt"], info["password"]):
            logger.info(f"successful login for user_id: {user.id}")
            token = auth.generate_jwt(user.id)

            # set cookie for response, browser will handle automatically
            response.set_cookie(
                key="access_token",
                value=token,
                httponly=True,  # prevent javascript access (xss protection)
                secure=True,  # only send over https
                samesite="lax"  # protect against csrf
            )

            response.status_code = status.HTTP_200_OK
        else:
            response.status_code = status.HTTP_401_UNAUTHORIZED

    except Exception:
        logger.info(f"user_id: {user.id} not found!")
        response.status_code = status.HTTP_404_NOT_FOUND

@user_router.get("")
def get_user(target_user_id: int, con: sqlite3.Connection = Depends(db.get_db), user_id = Depends(auth.validate_user_cookie)):
    return db.get_user_info(con, target_user_id, user_id)

@user_router.post("/add_friend")
def add_friend(target_user_id: int, con: sqlite3.Connection = Depends(db.get_db), user_id = Depends(auth.validate_user_cookie)):
    try:
        assert target_user_id != user_id
        db.add_friend(con, min(target_user_id, user_id), max(target_user_id, user_id))
    except:
        pass
