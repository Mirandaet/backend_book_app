from datetime import timedelta, timezone
import datetime
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

load_dotenv(override=True)

secret_key = os.getenv("SECRET_KEY")
access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
algorithm = os.getenv("ALGORITHM")
email_reset_token_expire_hours = int(os.getenv("EMAIL_RESET_TOKEN_EXPIRE_HOURS"))

def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=email_reset_token_expire_hours)
    now = datetime.datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        secret_key,
        algorithm=algorithm,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=algorithm)
        return str(decoded_token["sub"])
    except JWTError:
        return None