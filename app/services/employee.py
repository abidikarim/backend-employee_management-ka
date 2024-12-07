import uuid
from sqlalchemy import func
from sqlalchemy.orm import Session
from app import models, schemas
from app.OAuth2 import hash_password, verify_password
from app.utilities import send_mail
from app.enums import AccountStatus, TokenStatus
from fastapi import HTTPException, status
from .error import get_error_detail, add_error
from fastapi.responses import JSONResponse
from datetime import datetime
from app.dependencies import PaginationParams

error_keys = {
    "ck_employees_cnss_number": {
        "message": "-It should be {8 digits}-{2 digits} and it's mandatory if contract type Cdi or Cdd",
        "status": 400,
    },
    "employees_email_key": {"message": "Email already used", "status": 409},
    "employees_number_key": {"message": "Number should be unique", "status": 409},
    "Username and Password not accepted": {
        "message": "Email credentials not accepted",
        "status": 406,
    },
    "employees_pkey": {"message": "Employee not found", "status": 404},
    "unique_employee_role": {
        "message": "This employee already has this role",
        "status": 409,
    },
}


def convert_employee_to_schema(employee: models.Employee):
    return schemas.EmployeeOut(
        id=employee.id,
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        number=employee.number,
        birth_date=employee.birth_date,
        address=employee.address,
        cnss_number=employee.cnss_number,
        contract_type=employee.contract_type,
        gender=employee.gender,
        phone_number=str(employee.phone_number),
        roles=[employee_role.role for employee_role in employee.roles],
        account_status=employee.account_status,
        created_on=employee.created_on,
    )


def div_ciel(nominater, denominater):
    full_pages = nominater // denominater
    additional_page = 1 if nominater % denominater > 0 else 0
    return full_pages + additional_page


def add_confirmation_code(db: Session, db_employee: models.Employee):
    activation_code = models.AccountActivation(
        employee_id=db_employee.id, email=db_employee.email, token=uuid.uuid4()
    )
    db.add(activation_code)
    return activation_code


def get_confirmation_code(code: str, db: Session):
    code_db = (
        db.query(models.AccountActivation)
        .filter(models.AccountActivation.token == code)
        .first()
    )
    if code_db:
        return code_db
    return None


def verify_confirmation_code(code: str, db: Session):
    code_db = get_confirmation_code(code, db)
    if not code_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token not found"
        )
    emp_db = get_employee_by_email(code_db.email, db)
    if emp_db is None or emp_db.id != code_db.employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token"
        )
    if code_db.status == TokenStatus.Used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token already used"
        )
    if (datetime.now() - code_db.created_on.replace(tzinfo=None)).days > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired"
        )
    return code_db


def get_all(db: Session, pg_params: PaginationParams):
    try:
        skip = pg_params.limit * (pg_params.page - 1)
        query = db.query(models.Employee)
        if pg_params.name != None:
            query = query.filter(
                func.lower(
                    func.concat(
                        models.Employee.first_name, " ", models.Employee.last_name
                    )
                ).contains(func.lower(pg_params.name))
            )
        total_records = query.count()
        total_pages = div_ciel(total_records, pg_params.limit)
        result = query.limit(pg_params.limit).offset(skip).all()
        return {
            "total_records": total_records,
            "total_pages": total_pages,
            "employees": result,
        }
    except Exception as error:
        error_detail = get_error_detail(str(error), error_keys)
        raise HTTPException(
            status_code=error_detail["status"],
            detail=error_detail["message"],
        )


def get_employee_by_id(id: int, db: Session):
    try:
        employee = db.query(models.Employee).filter(models.Employee.id == id).first()
        if not employee:
            return None
    except Exception as error:
        error_detail = get_error_detail(str(error), error_keys)
        raise HTTPException(
            status_code=error_detail["status"],
            detail=error_detail["message"],
        )
    return employee


def get_employee_by_email(email: str, db: Session):
    try:
        employee = (
            db.query(models.Employee).filter(models.Employee.email == email).first()
        )
        if not employee:
            return None
    except Exception as error:
        error_detail = get_error_detail(str(error), error_keys)
        raise HTTPException(
            status_code=error_detail["status"],
            detail=error_detail["message"],
        )
    return employee


async def create_employee(employee_dict: dict, db: Session):
    try:
        roles = employee_dict.pop("roles")
        new_emp = models.Employee(**employee_dict)
        db.add(new_emp)
        db.flush()
        db.add_all(
            [models.EmployeeRole(role=role, employee_id=new_emp.id) for role in roles]
        )
        new_token = add_confirmation_code(db, new_emp)
        await send_mail(
            schemas.MailData(
                emails=[new_emp.email],
                body={
                    "name": f"{new_emp.first_name} {new_emp.last_name}",
                    "token": new_token.token,
                },
                template="confirm_account.html",
                subject="Confirm Account",
            )
        )
        db.commit()
        db.refresh(new_emp)
        return new_emp
    except Exception as error:
        db.rollback()
        add_error(text=str(error), db=db)
        error_detail = get_error_detail(str(error), error_keys)
        raise HTTPException(
            status_code=error_detail["status"],
            detail=error_detail["message"],
        )


async def edit_employee(employee_id: int, update_data: dict, db: Session):
    try:
        employee_to_update = get_employee_by_id(employee_id, db)
        if employee_to_update is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
            )
        if not verify_password(
            update_data["actual_password"], employee_to_update.password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong password"
            )
        {update_data.pop(key, None) for key in ["confirm_password", "actual_password"]}
        if update_data["password"] != None:
            update_data["password"] = hash_password(update_data["password"])
        for k, v in update_data.items():
            if v is None:
                update_data[k] = employee_to_update.__dict__[k]
        last_email = employee_to_update.email
        db.query(models.Employee).filter(models.Employee.id == employee_id).update(
            update_data, synchronize_session=False
        )
        db.flush()
        db.refresh(employee_to_update)
        if employee_to_update.email != last_email:
            new_token = add_confirmation_code(db, employee_to_update)
            await send_mail(
                schemas.MailData(
                    emails=[employee_to_update.email],
                    body={
                        "name": f"{employee_to_update.first_name} {employee_to_update.last_name}",
                        "token": new_token.token,
                    },
                    template="confirm_email.html",
                    subject="Confirm Email",
                )
            )
            employee_to_update.account_status = AccountStatus.Inactive
        db.commit()
        return employee_to_update
    except HTTPException as http_error:
        raise http_error
    except Exception as error:
        db.rollback()
        add_error(text=str(error), db=db)
        error_detail = get_error_detail(str(error), error_keys)
        raise HTTPException(
            status_code=error_detail["status"],
            detail=error_detail["message"],
        )


def confirmation_account(code: str, password: str, db: Session):
    try:
        code_db = verify_confirmation_code(code, db)
        db.query(models.Employee).filter(
            models.Employee.id == code_db.employee_id
        ).update(
            {
                "password": hash_password(password),
                "account_status": AccountStatus.Active.value,
            }
        )
        db.query(models.AccountActivation).filter(
            models.AccountActivation.id == code_db.id
        ).update({"status": TokenStatus.Used.value})
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Activation account successfully"},
        )
    except HTTPException as http_error:
        raise http_error
    except Exception as error:
        db.rollback()
        add_error(text=str(error), db=db)
        error_detail = get_error_detail(str(error), error_keys)
        raise HTTPException(
            status_code=error_detail["status"],
            detail=error_detail["message"],
        )


def confirmation_email(code: str, db: Session):
    try:
        code_db = verify_confirmation_code(code, db)
        db.query(models.Employee).filter(
            models.Employee.id == code_db.employee_id
        ).update({"account_status": AccountStatus.Active})
        code_db.status = TokenStatus.Used
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"message": "Email confirmed"}
        )
    except HTTPException as http_error:
        raise http_error
    except Exception as error:
        db.rollback()
        add_error(str(error), db)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
