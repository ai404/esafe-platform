from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


class AccountStatus(Base):
    """User's account status"""
    __tablename__ = 'account_status'

    id = Column(Integer, primary_key=True, autoincrement=True)
    status_name = Column(String(100), nullable=False)
    status_description = Column(Text)
    users = relationship("User", backref="account_status",
                         passive_deletes=True)

    def __repr__(self):
        return self.status_name
