from app.database import Base
from sqlalchemy import Column, String, Integer, TIMESTAMP, Enum, func, ForeignKey
from app.enums import TokenStatus


class ResetPassword(Base):
    __tablename__ = "reset_passwords"
    id = Column(Integer, nullable=False, primary_key=True)
    employee_id = Column(
        Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    email = Column(String, nullable=False)
    token = Column(String, nullable=False)
    status = Column(Enum(TokenStatus), default=TokenStatus.Pending.value)
    created_on = Column(TIMESTAMP(timezone=True), server_default=func.now())
