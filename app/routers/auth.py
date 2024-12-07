from fastapi import APIRouter, HTTPException
from app import schemas
from app.dependencies import dbDep, formDataDep
from app.services import auth

router = APIRouter(prefix="/auth", tags=["Authenticate"])


@router.post("/")
def login(
    employee_credentials: formDataDep,
    db: dbDep,
):
    return auth.login(
        employee_credentials={
            "email": employee_credentials.username,
            "password": employee_credentials.password,
        },
        db=db,
    )


@router.post("/resetpswd")
async def reset_pswd(email: schemas.ResetPassword, db: dbDep):
    return await auth.reset_password(email.email, db)


@router.patch("/createpswd")
def create_pswd(token: str, password_data: schemas.CreatePassword, db: dbDep):
    if password_data.password != password_data.confirm_password:
        raise HTTPException(status_code=400, detail="Password must be match")
    return auth.create_password(token, password_data.password, db)
