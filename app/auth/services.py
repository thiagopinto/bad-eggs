from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from passlib.context import CryptContext
from pydantic import UUID4
from app.user.models import Users
from app.client.models import Clients
from uuid import uuid4, UUID
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config import get_settings
from typing import Annotated

# from sqlmodel import Session, select

settings = get_settings()

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class Auth:
    @staticmethod
    async def authenticate(username: str, password: str):
        user = await Users.filter(username=username).first().prefetch_related("scopes")

        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        if not Users.verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        user_dict = user.dict()
        scopes = []

        for scope in user.scopes:
            scope_dict = scope.dict()
            scopes.append(scope_dict["name"])

        user_dict["scopes"] = scopes
        access_token = Auth.create_access_token(user_dict)
        refresh_token = Auth.create_refresh_token(user_dict)

        return JSONResponse({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }, status_code=200)

    @staticmethod
    async def authenticate_by_client(
        client_id: UUID, client_secret: str, username: str, password: str
    ):
        client = await Clients.filter(client_id=client_id).first()

        if client is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        if not Clients.verify_client_secret(client_secret, client.client_secret_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        return await Auth.authenticate(username=username, password=password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: int = None) -> str:
        to_encode = data.copy()

        if expires_delta is not None:
            access_token_expires = datetime.utcnow() + expires_delta
        else:
            access_token_expires = datetime.utcnow() + timedelta(
                minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )

        to_encode.update(
            {"exp": access_token_expires, "iss": settings.APP_NAME})
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, settings.TOKEN_ALGORITHM)

    @staticmethod
    def create_refresh_token(data: dict, expires_delta: int = None) -> str:
        to_encode = data.copy()

        if expires_delta is not None:
            refresh_token_expires = datetime.utcnow() + expires_delta
        else:
            refresh_token_expires = datetime.utcnow() + timedelta(
                minutes=int(settings.REFRESH_TOKEN_EXPIRE_MINUTES)
            )

        to_encode.update(
            {"exp": refresh_token_expires, "iss": settings.APP_NAME})
        return jwt.encode(
            to_encode, settings.JWT_REFRESH_SECRET_KEY, settings.TOKEN_ALGORITHM
        )

    @staticmethod
    async def refresh_token(refresh_token):
        payload = jwt.decode(
            refresh_token, settings.JWT_REFRESH_SECRET_KEY, settings.TOKEN_ALGORITHM
        )

        user = (
            await Users.filter(id=payload.get("id")).first().prefetch_related("scopes")
        )

        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        user_dict = user.dict()
        scopes = []

        for scope in user.scopes:
            scope_dict = scope.dict()
            scopes.append(scope_dict["name"])

        user_dict["scopes"] = scopes
        access_token = Auth.create_access_token(user_dict)
        refresh_token = Auth.create_refresh_token(user_dict)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    def get_confirmation_token(user_id: UUID4):
        jti = uuid4()
        claims = {"sub": user_id, "scope": "registration", "jti": jti}
        return {
            "jti": jti,
            "token": Auth.get_token(claims, settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        }


class Protect:
    @classmethod
    def check_token(
        cls,
        token: Annotated[
            str,
            Depends(
                OAuth2PasswordBearer(
                    tokenUrl="/auth/login",
                )
            ),
        ],
    ):
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, settings.TOKEN_ALGORITHM
            )
            scopes = payload.get("scopes")

            if scopes is not None:
                return scopes
        except JWTError:
            raise credentials_exception


class Mail:
    @staticmethod
    def send(name, email, text, html):
        sender = f"{settings.APP_NAME}: <{settings.MAIL_USERNAME}>"
        receiver = f"{name} <{email}>"

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Link"
        msg["From"] = sender
        msg["To"] = receiver

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        with smtplib.SMTP(settings.MAIL_HOST, int(settings.MAIL_PORT)) as server:
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.sendmail(sender, receiver, msg.as_string())
