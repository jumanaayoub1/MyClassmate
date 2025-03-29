import bcrypt


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
