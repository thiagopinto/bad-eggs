from jose import jwt
from uuid import uuid4
from datetime import datetime, timedelta
from app.config import get_settings
from app.user.models import Users
from app.auth.services import Mail as AuthMail

settings = get_settings()

class Mail:
    @staticmethod
    async def send_verify_email(id):
        user = await Users.get(id=id)
        user.verified_hash = str(uuid4())
        await user.save()

        access_token_expires = datetime.utcnow() + timedelta(
            minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        client_encode = {
            "user_id": user.id,
            "verified_hash": user.verified_hash,
            "exp": access_token_expires,
            "iss": settings.APP_NAME,
        }

        hash = jwt.encode(
            client_encode, settings.JWT_SECRET_KEY, settings.TOKEN_ALGORITHM
        )

        # Create the body of the message (a plain-text and an HTML version).
        text = """\
            Hi!\n
            How are you?\n
            this is an email verification from {app_name} click on the link to confirm:
            \n{app_url}/auth/verify/{hash}""".format(
            app_name=settings.APP_NAME, app_url=settings.APP_URL, hash=hash
        )

        html = """\
            <html>
            <head></head>
            <body>
                <p>Hi!</p>
                <p>How are you?</p>
                <p>
                    this is an email verification from {app_name} click on the link to 
                    confirm:
                    <a href="{app_url}/auth/verify/{hash}">Validate</a>
                </p>
            </body>
            </html>
            """.format(
            app_name=settings.APP_NAME, app_url=settings.APP_URL, hash=hash
        )

        AuthMail.send(user.name, user.username, text, html)

    @staticmethod
    def verify_email(token):
        try:
            token_dict = jwt.decode(
                token, settings.JWT_SECRET_KEY, settings.TOKEN_ALGORITHM
            )
            return token_dict
        except Exception as e:
            raise e
