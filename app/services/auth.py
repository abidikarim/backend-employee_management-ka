from datetime import datetime
import uuid
from fastapi.responses import JSONResponse
from app.enums import AccountStatus, TokenStatus
from fastapi import status, HTTPException
from sqlalchemy.orm import Session
from app.services import employee
from app import models, schemas
from app.OAuth2 import verify_password, create_access_token, hash_password
from app.services.error import add_error
from app.utilities import send_mail


def login(employee_credentials: dict, db: Session):
    try:
        emp = employee.get_employee_by_email(employee_credentials["email"], db)
        if emp is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Email not found"
            )
        if emp.account_status == AccountStatus.Inactive:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your account is inactive",
            )
        if not verify_password(employee_credentials["password"], emp.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong password"
            )
        access_token = create_access_token({"user_id": emp.id})
        return schemas.Token(access_token=access_token, token_type="Bearer")
    except HTTPException as http_error:
        raise http_error
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


async def reset_password(email: str, db: Session):
    try:
        emp = employee.get_employee_by_email(email, db)
        if emp is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Email not found"
            )
        new_token = models.ResetPassword(
            employee_id=emp.id,
            email=emp.email,
            token=uuid.uuid4(),
            status=TokenStatus.Pending,
        )
        db.add(new_token)
        db.flush()
        await send_mail(
            schemas.MailData(
                emails=[emp.email],
                body={
                    "name": f"{emp.first_name} {emp.last_name}",
                    "token": new_token.token,
                },
                template="reset_password.html",
                subject="Reset Password",
            )
        )
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Check your email to reset your password"},
        )
    except Exception as error:
        add_error(str(error), db)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


def create_password(code: str, password: str, db: Session):
    try:
        code_db = (
            db.query(models.ResetPassword)
            .filter(models.ResetPassword.token == code)
            .first()
        )
        if not code_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token not found",
            )
        emp_db = employee.get_employee_by_email(code_db.email, db)
        if not emp_db or emp_db.id != code_db.employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token"
            )
        if code_db.status == TokenStatus.Used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token already used",
            )
        if (datetime.now() - code_db.created_on.replace(tzinfo=None)).days > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token expired",
            )
        emp = (
            db.query(models.Employee)
            .filter(models.Employee.id == emp_db.id)
            .update({"password": hash_password(password)})
        )
        if not emp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset password failed try again",
            )
        code_db.status = TokenStatus.Used
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Reset password successfully"},
        )
    except HTTPException as http_error:
        raise http_error
    except Exception as error:
        add_error(str(error), db)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
