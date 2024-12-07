from typing import Optional

from fastapi import HTTPException

from app import models
from sqlalchemy.orm import Session


def get_error_detail(error: str, errors_keys: dict):
    for err in errors_keys:
        if err in error:
            return errors_keys[err]
    return dict({"message": "Somthing went wrong", "status": 400})


def add_error(text: str, db: Session, employee_id: Optional[int] = None):
    try:
        db.add(models.Error(text=text, employee_id=employee_id))
        db.commit()
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"Somthing went wrong")
