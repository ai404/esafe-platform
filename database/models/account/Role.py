from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


class Role(Base):
    """Assigned roles for users"""
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(100), nullable=False)
    role_description = Column(Text)
    users = relationship("User", backref="role", passive_deletes=True)

    def __init__(self, role_name, role_description):
        self.role_name = role_name
        self.role_description = role_description

    def _repr_name(self) -> str:
        return f"[{self.id}] {self.role_name}"


class Role_dict(object):
    """Different possible roles for users"""
    ADMIN = 3
    MANAGER = 2
    STAFF = 1
