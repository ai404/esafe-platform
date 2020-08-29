from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, expression

from database import Base, models
from config import Config

import uuid
import os


class Location(Base):
    """Define locations within a company"""
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    location_name = Column(String(200), nullable=False)
    location_description = Column(Text)
    location_address = Column(String(200))
    location_plan = Column(Text)
    lat = Column(Float)
    lng = Column(Float)
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(),
                        server_onupdate=func.now())

    company_id = Column(ForeignKey(
        'companies.id', ondelete='CASCADE'), nullable=False)
    entities = relationship("Entity", backref="location", passive_deletes=True)
    users = relationship("User", secondary="accesses")

    @property
    def name(self) -> str:
        return self.location_name

    @property
    def description(self) -> str:
        return self.location_description

    @property
    def address(self) -> str:
        return self.location_address

    def alerts_count(self, alert_type=None) -> int:
        return sum(map(lambda x: x.alerts_count(alert_type), self.entities))

    @property
    def cameras_count(self) -> int:
        return sum(map(lambda x: x.cameras_count, self.entities))

    @property
    def active_cameras_count(self) -> int:
        return sum(map(lambda x: x.active_cameras_count, self.entities))

    @property
    def entities_count(self) -> int:
        return len(self.entities)

    @property
    def plan(self) -> str:
        """A url to the location image 2D Plan"""
        if self.location_plan:
            return os.path.join(Config.UPLOAD_URL, "plans", self.location_plan)
        return ""

    @plan.setter
    def plan(self, plan):
        """Setter for the location's plan"""
        self.location_plan = plan

    def get_cameras_coordiantes(self) -> str:
        """A concatenated string of cameras coordinates"""
        return "|".join([entity.get_cameras_coordiantes() for entity in self.entities])

    def get_boxes(self):
        """Returns a list of entities boundaries"""
        boxes = []
        for ent in self.entities:
            boxes += ent.get_boxes()
        return boxes

    def _repr_name(self) -> str:
        return f"[{self.id}] {self.location_name}"