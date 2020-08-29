from sqlalchemy import Column, Integer, DateTime, Text, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression, text, func

from ._device import Device


class Camera(Device):
    __tablename__ = 'cameras'

    cam_type = Column(String(20))
    orientation = Column(String(100))
    v_units = Column(Float)
    h_units = Column(Float)
    notif_min_units = Column(Float)

    width = Column(Float, server_default=text("1280"))
    height = Column(Float, server_default=text("720"))
    
    entity_id = Column(ForeignKey('entities.id', ondelete='CASCADE'), nullable=False)

    users = relationship("User",secondary="accesses")
    alerts = relationship("Alert",backref="camera",passive_deletes=True)

    @property
    def entity_name(self):
        return self.entity.name
    
    @property
    def location_name(self):
        return self.entity.location_name
    
    def get_name(self):
        return f"Camera{self.id}"