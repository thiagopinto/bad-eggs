from jose import jwt
from uuid import uuid4
from datetime import datetime, timedelta
from app.config import get_settings
from app.client.models import Clients
from app.auth.services import Mail as AuthMail
#from sqlmodel import Session

settings = get_settings()

class Mail:
    @staticmethod
    async def send_verify_email(id):
        client = await Clients.get(id=id)
        client.verified_hash = str(uuid4())
        await client.save()

        access_token_expires = datetime.utcnow() + timedelta(
            minutes=int(settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        )

        client_encode = {
            "client_id": client.id,
            "verified_hash": client.verified_hash,
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
            \n{app_url}/auth/client/verify/{hash}""".format(
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
                    confirm:<a href="{app_url}/auth/client/verify/{hash}">Validate</a>
                </p>
            </body>
            </html>
            """.format(
            app_name=settings.APP_NAME, app_url=settings.APP_URL, hash=hash
        )

        AuthMail.send(client.name, client.responsible_email, text, html)

    @staticmethod
    def verify_email(token):
        try:
            token_dict = jwt.decode(
                token, settings.JWT_SECRET_KEY, settings.TOKEN_ALGORITHM
            )
            return token_dict
        except Exception as e:
            raise e
