from app.database import Base
from sqlalchemy import (
    Column,
    String,
    Integer,
    TIMESTAMP,
    DATE,
    Enum,
    func,
    CheckConstraint,
)
from app.enums import Gender, AccountStatus, ContractType
from sqlalchemy.orm import relationship


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, nullable=False, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=True)
    number = Column(Integer, nullable=False, unique=True)
    birth_date = Column(DATE, nullable=True)
    address = Column(String, nullable=True)
    cnss_number = Column(String, nullable=True)
    contract_type = Column(Enum(ContractType), nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    account_status = Column(
        Enum(AccountStatus),
        default=AccountStatus.Inactive.value,
        nullable=False,
    )
    phone_number = Column(String, nullable=True)
    created_on = Column(TIMESTAMP(timezone=True), server_default=func.now())
    __table_args__ = (
        CheckConstraint(
            "(contract_type IN ('Cdi','Cdd') AND cnss_number IS NOT NULL AND cnss_number ~ '^\\d{8}-\\d{2}$') OR (contract_type IN ('Apprenti','Sivp') AND (cnss_number is NULL OR  cnss_number ~ '^\\d{8}-\\d{2}$'))",
            name="ck_employees_cnss_number",
        ),
    )
    roles = relationship("EmployeeRole")
