from typing import List
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from starlette.responses import JSONResponse
from ..config import settings
from pathlib import Path
from app import schemas

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM_NAME=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "../templates",
)


async def send_mail(mail_data: schemas.MailData) -> JSONResponse:

    message = MessageSchema(
        subject=mail_data.model_dump().get("subject"),
        recipients=mail_data.model_dump().get("emails"),
        template_body=mail_data.model_dump().get("body"),
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name=mail_data.model_dump().get("template"))
    return JSONResponse(status_code=200, content={"message": "email has been sent"})
