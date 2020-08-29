from sqlalchemy import Column, Integer, DateTime, String, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, expression

from database import Base


class Company(Base):
    """Companies model used to assign users and limit their scope"""
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(200), nullable=False)
    company_description = Column(Text)
    company_phone = Column(String(20))
    is_active = Column(Boolean, server_default=expression.true())
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(),
                        server_onupdate=func.now())

    employees = relationship("User", backref="company", passive_deletes=True)
    locations = relationship(
        "Location", backref="company", passive_deletes=True)

    def _repr_name(self) -> str:
        return f"[{self.id}] {self.company_name}"