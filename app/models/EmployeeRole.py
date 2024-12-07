from app.database import Base
from sqlalchemy import Column, Integer, Enum, ForeignKey, UniqueConstraint
from app.enums import Role


class EmployeeRole(Base):
    __tablename__ = "employee_roles"
    id = Column(Integer, nullable=False, primary_key=True)
    employee_id = Column(
        Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    role = Column(Enum(Role), nullable=False)
    __table_args__ = (
        UniqueConstraint("employee_id", "role", name="unique_employee_role"),
    )
