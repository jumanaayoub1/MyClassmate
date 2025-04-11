from fastapi import APIRouter, Depends, status, Response
import sqlite3
from pydantic import BaseModel

import db
import auth

import logging
logger = logging.getLogger(__name__)

user_router = APIRouter(prefix="/user", tags=["user"])
classes_router = APIRouter(prefix="/classes", tags=["classes"])

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
                secure=False,  # only send over https
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

class AddFriendModel(BaseModel):
    target_user: int

@user_router.post("/friends/add")
def add_friend(params: AddFriendModel, con: sqlite3.Connection = Depends(db.get_db), user_id = Depends(auth.validate_user_cookie)):
    try:
        assert params.target_user != user_id
        db.add_friend(con, user_id, params.target_user)
    except:
        pass

@user_router.post("/friends/accept")
def accept_friend(params: AddFriendModel, con: sqlite3.Connection = Depends(db.get_db), user_id = Depends(auth.validate_user_cookie)):
    try:
        assert params.target_user != user_id
        db.accept_friend(con, user_id, params.target_user)
    except:
        pass


class EnrollModel(BaseModel):
    major: str
    code: int
    section: int

@classes_router.post("/enroll")
def enroll_class(params: EnrollModel, con: sqlite3.Connection = Depends(db.get_db), user_id = Depends(auth.validate_user_cookie)):
    major = params.major.upper()
    class_id = db.possibly_create_class_and_get_id(con, major, params.code, params.section)
    
    try:
        db.enroll_in_class(con, user_id, class_id)
    except:
        pass
