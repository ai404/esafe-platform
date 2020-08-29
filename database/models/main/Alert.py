from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, and_, desc

from database import Base, db_session

from database.models.main.Entity import Entity


class Alert(Base):
    """Generated Alerts by inference service."""
    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_type = Column(String(20), nullable=False)
    source_id = Column(String(20), nullable=False)
    description = Column(String(200))

    camera_id = Column(ForeignKey(
        'cameras.id', ondelete='CASCADE'), nullable=True)
    entity_id = Column(ForeignKey(
        'entities.id', ondelete='CASCADE'), nullable=False)
    first_party_id = Column(String(100))
    second_party_id = Column(String(100))

    created_on = Column(DateTime, server_default=func.now())

    @classmethod
    def get_alerts(cls, id=None, for_name=None, offset=None, limit=10):
        """Get alert of the given entity/location.

        Args:
            id (int, optional): Id of the targeted entity/location. Defaults to None.
            for_name (str, optional): Specify the targeted object name (entity/location). Defaults to None.
            offset (int, optional): Selection Offset. Defaults to None.
            limit (int, optional): The number of records to return. Defaults to 10.

        Returns:
            list: List of Alerts that belongs to the given Entity / Location.
        """
        query = Alert.query

        if for_name == "entity":
            query_filter = Alert.entity_id == id
        elif for_name == "location":
            query = Alert.query.join(Entity)
            query_filter = Entity.location_id == id
        else:
            return []

        if offset is not None and offset > 0:
            query_filter = and_(Alert.id < offset, query_filter)

        query = query.filter(query_filter).order_by(desc(Alert.id))

        if limit is not None:
            query = query.limit(limit)

        return query.all()