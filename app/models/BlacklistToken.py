from app.database import Base
from sqlalchemy import Integer, String, Column, PrimaryKeyConstraint


class BlacklistToken(Base):
    __tablename__ = "blacklist_tokens"
    id = Column(Integer, nullable=False, primary_key=True)
    token = Column(String, nullable=False)
    PrimaryKeyConstraint("id")
