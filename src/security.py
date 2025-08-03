import bcrypt


# Hash a password using bcrypt and return as string (for DB storage)
def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
    return hashed_password.decode("utf-8")  # convert bytes to str for storage


# Check if the provided password matches the hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_byte_enc = plain_password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_byte_enc, hashed_password_bytes)
