from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func

from database import Base


class Access(Base):
    """Access records for users"""
    __tablename__ = 'accesses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)
    camera_id = Column(ForeignKey('cameras.id', ondelete='CASCADE'))
    entity_id = Column(ForeignKey('entities.id', ondelete='CASCADE'))
    location_id = Column(ForeignKey('locations.id', ondelete='CASCADE'))
    access_type = Column(Integer, server_default="1")
    created_on = Column(DateTime, server_default=func.now())
