from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import func

from database import Base


class Profile(Base):
    """User profile"""
    __tablename__ = 'profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(200), nullable=False)
    last_name = Column(String(200), nullable=False)
    phone = Column(String(20))
    picture = Column(Text)
    user_id = Column(ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(),
                        server_onupdate=func.now())

    def __init__(self, first_name, last_name, user_id):
        self.first_name = first_name
        self.last_name = last_name
        self.user_id = user_id

    def get_picture(self) -> str:
        """Returns User profile picture"""
        return self.picture if self.picture else "user.png"
    
    def _repr_name(self) -> str:
        return f"[{self.id}] {self.first_name} {self.last_name}"