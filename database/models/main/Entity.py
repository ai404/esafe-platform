from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, expression

from database import Base, db_session, models


class Entity(Base):
    """Define entities within a location"""
    __tablename__ = 'entities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    description = Column(String(200))
    bounding_box = Column(Text)

    location_id = Column(ForeignKey(
        'locations.id', ondelete='CASCADE'), nullable=False)

    created_on = Column(DateTime, server_default=func.now())
    alerts = relationship("Alert", backref="entity", passive_deletes=True)
    cameras = relationship("Camera", backref="entity", passive_deletes=True)

    @property
    def address(self) -> str:
        """Dot walk to get location's name."""
        return self.location.name

    def alerts_count(self, alert_type: str = None):
        """Get the number of alerts for the given type within the requested entity

        Args:
            alerts_type (str): A Type of alerts to count

        Returns:
            int: Alerts Count
        """
        _filter = {"entity_id": self.id}
        if alert_type is not None:
            _filter["alert_type"] = alert_type

        q = models.Alert.query.filter_by(**_filter)
        return db_session().execute(q.statement.with_only_columns([func.count()]).order_by(None)).scalar()

    @property
    def active_cameras(self) -> list:
        """A list of active Cameras assigned to this entity"""
        return list(filter(lambda x: x.active, self.cameras))

    @property
    def active_cameras_count(self) -> int:
        """Count active cameras for this entity"""
        return len(self.active_cameras)

    @property
    def cameras_count(self) -> int:
        """Count active cameras for this entity"""
        return len(self.cameras)

    def get_boxes(self) -> list:
        """A list of bounding box coordinates"""
        return [self.bounding_box] if self.bounding_box else []

    @property
    def plan(self) -> str:
        """A url to the location image 2D Plan"""
        return self.location.plan

    @property
    def location_name(self) -> str:
        """Entity's parent Location name"""
        return self.location.location_name

    def get_cameras_coordiantes(self) -> str:
        """A concatenated string of cameras coordinates"""
        return "|".join([camera.coordinates for camera in self.cameras if camera.coordinates is not None])

    def _repr_name(self) -> str:
        return f"[{self.id}] {self.name}"
