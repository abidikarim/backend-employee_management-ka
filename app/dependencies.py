from fastapi import Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app import models
from app.OAuth2 import get_current_employee
from app.database import get_db
from sqlalchemy.orm import Session

dbDep = Annotated[Session, Depends(get_db)]
formDataDep = Annotated[OAuth2PasswordRequestForm, Depends()]


class PaginationParams:
    def __init__(self, name: str = None, page: int = 1, limit: int = 100):
        self.name = name
        self.page = page
        self.limit = limit


pagination_params = Annotated[PaginationParams, Depends()]

oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")
tokenDep = Annotated[str, Depends(oauth_scheme)]


def get_curr_emp(db: dbDep, token: tokenDep):
    return get_current_employee(db, token)


currentEmployee = Annotated[models.Employee, Depends(get_curr_emp)]
