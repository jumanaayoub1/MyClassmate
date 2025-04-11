import sqlite3
import random
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
            id INTEGER PRIMARY KEY,
            major_code TEXT NOT NULL,
            class_code INTEGER NOT NULL,
            section INTEGER NOT NULL,

            UNIQUE (major_code, class_code, section)
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
            pending_user_id INTEGER,

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


def get_user_info(db: sqlite3.Connection, target_id: int, source_id: int):
    cursor = db.cursor()
    cursor.execute(
    """
        SELECT * FROM users
        WHERE id = ?
        AND (
            privacy = 'public'
            OR EXISTS (
                SELECT 1 FROM users_friendships_junction
                WHERE
                    (user_id1 = ? AND user_id2 = ? AND pending_user_id IS NULL)
            )
        )
        """,
        (target_id, min(source_id, target_id), max(target_id, source_id)),
        )
    return cursor.fetchone()


def default_username():
    '''
    generate a random username
    format: <adjective><noun><number>
    currently has 8 * 6 * 100 = 4800 possibilities
    '''
    possible_first_word = ["cool", "silly", "funny", "red", "blue", "smart", "tall", "short"]
    possible_second_word = ["dog", "cat", "bird", "spartan", "student", "academic"]

    adjective = random.choice(possible_first_word)
    noun = random.choice(possible_second_word)
    number = str(random.randint(0, 99)) # cast to string to append

    return adjective + noun + number


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


def add_friend(db: sqlite3.Connection, user_a: int, user_b: int):
    cursor = db.cursor() 
    cursor.execute("""
        INSERT INTO users_friendships_junction (user_id1, user_id2, pending_user_id)
        VALUES (?, ?, ?)
    """, (min(user_a, user_b), max(user_a, user_b), user_b)
    )
    db.commit()


def accept_friend(db: sqlite3.Connection, user_a, user_b: int) -> None:
    cursor = db.cursor()
    cursor.execute("""
        UPDATE users_friendships_junction
        SET pending_user_id = NULL
        WHERE user_id1 = (?) AND user_id2 = (?)
    """, (min(user_a, user_b), max(user_a, user_b))
    )
    db.commit()

def possibly_create_class_and_get_id(
        db: sqlite3.Connection,
        major: str,
        code: int,
        section: int
) -> int: 
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO classes (major_code, class_code, section)
        VALUES (?, ?, ?)
        ON CONFLICT (major_code, class_code, section) DO NOTHING
    """, (major, code, section)
    )
    db.commit()

    cursor.execute("""
        SELECT id FROM classes
        WHERE major_code = ? AND class_code = ? AND section = ?
    """, (major, code, section)
    )

    return cursor.fetchone()[0]

def enroll_in_class(
    db: sqlite3.Connection,
    user_id: int,
    class_id: int
):
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO users_classes_junction (user_id, class_id)
        VALUES (?, ?)
        ON CONFLICT (PRIMARY KEY) DO NOTHING
    """, (user_id, class_id)
    )
    db.commit()

def update_user_fields(
    db: sqlite3.Connection,
    user_id: int,
    update: dict
):
    cursor = db.cursor()

    fields = [field for field in update]
    values = [update[field] for field in fields] + [str(user_id)]
    clause = ', '.join([f"{x} = ?" for x in fields])

    query = f"UPDATE users SET {clause} WHERE id = ?"
    cursor.execute(query, values) 
    db.commit()
