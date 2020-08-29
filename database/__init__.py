from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy_utils import database_exists, create_database

from config import Config

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI
)
if not database_exists(engine.url):
    create_database(engine.url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

BaseQuery = declarative_base()
BaseQuery.query = db_session.query_property()


class Base(BaseQuery):
    __abstract__ = True

    def _repr_name(self):
        return self.id
        
    def __repr__(self):
        return f"{self.__class__.__name__} {self._repr_name()}"

from .models import *

BaseQuery.metadata.create_all(engine)
