from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from app.enums import (
    Gender,
    AccountStatus,
    ContractType,
    Role,
    FieldType,
    MatchyComparer,
    ConditionProperty,
)
from typing import List, Dict, Any, Optional


class OurBaseModel(BaseModel):
    class Config:
        from_attributes = True


class PagedResponse(OurBaseModel):
    page_number: int
    page_size: int
    total_pages: int
    total_records: int


class BaseOut(OurBaseModel):
    detail: str
    status_code: int


class EmployeeBase(OurBaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    number: int
    birth_date: date | None = None
    address: str | None = None
    cnss_number: str | None = None
    contract_type: ContractType
    gender: Gender
    phone_number: str | None = None
    roles: List[Role]


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(OurBaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    number: int | None = None
    birth_date: date | None = None
    address: str | None = None
    cnss_number: str | None = None
    contract_type: ContractType | None = None
    gender: Gender | None = None
    phone_number: str | None = None
    password: str | None = None
    confirm_password: str | None = None
    actual_password: str


class EmployeeOut(EmployeeBase):
    id: int
    account_status: AccountStatus
    created_on: datetime


class EmployeesOut(PagedResponse):
    employees: List[EmployeeOut]


class ResetPassword(OurBaseModel):
    email: EmailStr


class Token(OurBaseModel):
    access_token: str
    token_type: str


class TokenData(OurBaseModel):
    id: int


class MailData(OurBaseModel):
    emails: List[EmailStr]
    body: Dict[str, Any]
    template: str
    subject: str


class CreatePassword(OurBaseModel):
    password: str
    confirm_password: str


class confirmationCode(OurBaseModel):
    code: str


class MatchyCondition(OurBaseModel):
    property: ConditionProperty
    comparer: Optional[MatchyComparer] = None
    value: int | float | str | List[str]
    custom_fail_message: Optional[str] = None


class MatchyOption(OurBaseModel):
    display_value: str
    value: Optional[str] = None
    mandatory: Optional[bool] = False
    type: FieldType
    conditions: Optional[List[MatchyCondition]] = []


class ImportPossibleFields(OurBaseModel):
    possible_fields: List[MatchyOption] = []


class MatchyCell(OurBaseModel):
    colIndex: int
    rowIndex: int
    value: str


class UploadEntry(OurBaseModel):
    lines: List[Dict[str, MatchyCell]]
    force_upload: Optional[bool] = False


class MatchyWrongCell(OurBaseModel):
    message: str
    rowIndex: int
    colIndex: int


class ImportResponse(BaseOut):
    errors: Optional[str] = None
    warnings: Optional[str] = None
    wrongCells: Optional[List[MatchyWrongCell]] = None
