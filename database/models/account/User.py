import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression, func, text

from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import and_

from flask import render_template, flash, url_for

from database import models, db_session, Base


class User(Base):
    """User model"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)

    email = Column(String(200), nullable=False, unique=True)
    password = Column(Text, nullable=False)
    last_login = Column(DateTime)
    confirmed = Column(Boolean, server_default=expression.false())
    confirmed_on = Column(DateTime)
    approved = Column(Boolean, server_default=expression.false())
    aggrement_accepted = Column(Boolean, server_default=expression.false())
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(),
                        server_onupdate=func.now())

    account_status_id = Column(ForeignKey(
        "account_status.id", ondelete='CASCADE'), server_default=text("'1'"))

    is_su = Column(Boolean, server_default=expression.false())
    role_id = Column(ForeignKey('roles.id', ondelete='CASCADE'),
                     server_default=text("'1'"))
    company_id = Column(ForeignKey(
        'companies.id', ondelete='CASCADE'), nullable=True)
    manager_id = Column(ForeignKey('users.id'), nullable=True)

    profile = relationship("Profile", backref="user",
                           uselist=False, passive_deletes='all')

    assigned_locations = relationship("Location", secondary="accesses")

    def __init__(self, email=None, password=None, confirmed=False):
        if email:
            self.email = email
        if password:
            self.set_password(password)

        self.confirmed = confirmed
        if confirmed:
            self.confirmed_on = datetime.datetime.now()

    def set_password(self, password):
        """Hash password before saving"""
        self.password = generate_password_hash(password)

    def get_id(self):
        return self.id

    @property
    def first_name(self):
        if self.profile:
            return self.profile.first_name

    @first_name.setter
    def first_name(self, fname):
        if self.profile:
            self.profile.first_name = fname

    @property
    def last_name(self):
        if self.profile:
            return self.profile.last_name

    @last_name.setter
    def last_name(self, lname):
        if self.profile:
            self.profile.last_name = lname

    @property
    def locations(self):
        """Return a list of locations visible to the User"""
        if self.role_id <= models.Role_dict.MANAGER:
            return self.assigned_locations
        elif self.role_id == models.Role_dict.ADMIN:
            return self.company.locations

    @property
    def entities(self):
        """Return a list of entities visible to the User."""
        items = []

        for location in self.locations:
            items += location.entities

        return items

    @property
    def cameras(self):
        """Yields a list of cameras visible to the User"""
        for entity in self.entities:
            for camera in entity.cameras:
                yield camera

    @property
    def staff(self):
        """Returns accounts administred by current User"""
        if self.role_id == models.Role_dict.ADMIN:
            return User.query.filter(and_(User.company_id == self.company_id, User.id != self.id)).all()
        elif self.role_id == models.Role_dict.MANAGER:
            loc_ids = list(map(lambda x: x.id, self.locations))
            _filter = and_(User.role_id == models.Role_dict.STAFF,
                           models.Location.id.in_(loc_ids))
            return User.query.join(models.Access).join(models.Location).filter(_filter).all()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def init_folders(self):
        try:
            os.makedirs("media/users/{id}/pictures".format(id=self.id))
        except:
            pass

    @classmethod
    def authenticate(cls, username, password):
        """Verify User credentials and authentucate"""
        user = User.query.filter_by(email=username).first()
        if user and check_password_hash(user.password, password):
            return user
        return None

    @classmethod
    def identity(cls, payload):
        return User.query.filter(User.id == payload['identity']).scalar()

    def _repr_name(self) -> str:
        return f"[{self.id}] {self.email}"