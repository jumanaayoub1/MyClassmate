import sqlite3
import auth
from enum import Enum


class UserPrivacy(Enum):
    PRIVATE = "private"
    PUBLIC = "public"


def _make_tables(db: sqlite3.Connection):
    cursor = db.cursor()
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            salt TEXT NOT NULL,
            password TEXT NOT NULL,
            privacy TEXT NOT NULL,
            major TEXT
        );

        -- heres an example:
        -- CMPE-131 Sec 01
        -- major_code: CMPE
        -- class_code: 131
        -- section: 01
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            major_code TEXT NOT NULL,
            class_code TEXT NOT NULL,
            section TEXT NOT NULL 
        );

        CREATE TABLE IF NOT EXISTS users_classes_junction (
            user_id INTEGER NOT NULL,
            class_id INTEGER NOT NULL,

            PRIMARY KEY (user_id, class_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(class_id) REFERENCES classes(id)
        );

        CREATE TABLE IF NOT EXISTS users_friendships_junction (
            user_id1 INTEGER NOT NULL,
            user_id2 INTEGER NOT NULL,

            PRIMARY KEY (user_id1, user_id2),
            FOREIGN KEY(user_id1) REFERENCES users(id),
            FOREIGN KEY(user_id2) REFERENCES users(id),
            CHECK (user_id1 < user_id2) -- for consistent ordering
        );
    """
    )


def get_db():
    db = sqlite3.connect("database.db")

    # make sure tables exist
    _make_tables(db)

    db.row_factory = sqlite3.Row
    try:
        yield db
    finally:
        db.close()


def get_user_info(db: sqlite3.Connection, target_id: int):
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT * FROM users WHERE users.id = (?)
    """,
        (target_id,),
    )
    return cursor.fetchall()


# TODO: generate a random username as a placeholder
def default_username():
    return ""


def insert_user(
    db: sqlite3.Connection,
    user_id,
    user_password,
    username=None,
    privacy=None,
    major=None,
):
    salt, password = auth.hash_password(user_password)

    if username is None:
        username = default_username
    if privacy is None:
        privacy = UserPrivacy.PRIVATE.value
    if major is None:
        major = ""

    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO users (id, username, salt, password, privacy, major)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, username, salt, password, privacy, major),
    )
    db.commit()

def get_login_info(db: sqlite3.Connection, user_id: int):
    cursor = db.cursor()
    cursor.execute("""
        SELECT u.salt, u.password
        FROM users u
        WHERE u.id = (?)
                   """, (user_id, ))
    return cursor.fetchone()

