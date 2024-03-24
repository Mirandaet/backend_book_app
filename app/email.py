from datetime import timedelta, timezone
import datetime
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv(override=True)

secret_key = os.getenv("SECRET_KEY")
access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
algorithm = os.getenv("ALGORITHM")
email_reset_token_expire_hours = int(os.getenv("EMAIL_RESET_TOKEN_EXPIRE_HOURS"))
postmark_token = os.getenv("POSTMARK_TOKEN")

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
    

def send_password_reset_email(email: str, token: str):
    reset_url = f"http://localhost:5173/resetpassword?token={token}"
    message = {
        "From": "mailer@valutaomvandla.com",
        "To": email,
        "Subject": "Password Reset Request",
        "HtmlBody": f'<strong>You have requested to reset your password.</strong> Please click on the link to reset your password: <a href="{reset_url}">Reset Password</a>',
        "MessageStream": "outbound"
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Postmark-Server-Token": f"{postmark_token}"
    }

    try:
        response = requests.post(
            "https://api.postmarkapp.com/email", headers=headers, data=json.dumps(message))
        response.raise_for_status()  
        print(f"Email sent to {email}: {response.status_code}")
        print(response.json())
    except requests.exceptions.HTTPError as e:
        print(f"Failed to send email to {email}, HTTP error: {e}")
        try:
            print(e.response.json())
        except ValueError:  
            print("Error response content is not JSON")
    except Exception as e:
        print(f"Failed to send email to {email}: {e}")