from sqlalchemy import Column, Integer, DateTime, Text, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression, text, func

from database import Base

class Device(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    streaming_uri = Column(String(200), nullable=False)
    device_metadata = Column(String(200))
    coordinates = Column(String(100))

    description = Column(Text)
    
    active = Column(Boolean, server_default=expression.false())
    streaming_output = Column(Boolean, server_default=expression.false())
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    
    @classmethod
    def get_active(cls):
        return cls.query.filter(cls.active == True).all()

    @classmethod
    def get_all(cls):
        return cls.query.all()