import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression, func

from database import Base


class Token(Base):
    """Generated Tokens for user identity verification"""
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    token_value = Column(String(200), nullable=False)
    user_id = Column(ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)
    created_on = Column(DateTime, server_default=func.now())
    expires_on = Column(DateTime, default=lambda x: datetime.datetime.now(
    ) + datetime.timedelta(minutes=60))
    used = Column(Boolean, server_default=expression.false())

    def __init__(self, user_id, token):
        self.token_value = token
        self.user_id = user_id
