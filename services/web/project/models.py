from sqlalchemy import Column, DateTime, ForeignKey, Boolean, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, desc

from . import db


def get_all_user():
    users = UserTbl.query.order_by(desc(UserTbl.is_active)).all()
    return users


def get_all_active_user():
    users = UserTbl.query.filter_by(is_active=True).order_by(desc(UserTbl.is_active)).all()
    return users


def get_limit_user(limit):
    users = UserTbl.query.filter_by(is_active=True).order_by(desc(UserTbl.is_active)).limit(limit).all()
    return users


def get_user_name(user_id):
    user_info = db.session.query(UserTbl).filter_by(user_id=user_id)
    user_name = ""
    for user in user_info:
        user_name = user.name
    return user_name


def get_user_role(user_id):
    user_info = db.session.query(UserTbl).filter_by(user_id=user_id)
    user_role = ""
    for user in user_info:
        user_role = user.role
    return user_role


def get_account_status(user_id):
    user_info = db.session.query(UserTbl).filter_by(user_id=user_id)
    account_status = ""
    for user in user_info:
        account_status = user.is_active
    return account_status


def get_user_desc(user_id):
    user_info = db.session.query(UserTbl).filter_by(user_id=user_id)
    user_desc = ""
    for user in user_info:
        user_desc = user.description
    return user_desc


def get_total_user(*args):
    if args:
        total_user = UserTbl.query.filter_by(is_active=True).count()
    else:
        total_user = UserTbl.query.count()
    return total_user


def get_first_user():
    user_first = UserTbl.query.order_by(desc(UserTbl.is_active)).first()
    return user_first


def update_user(user_name, data_update):
    db.session.query(UserTbl).filter_by(name=user_name).update(data_update)
    db.session.commit()


def is_exist_user_name(user_name):
    is_exists = db.session.query(UserTbl).filter(UserTbl.name == user_name).first()
    return is_exists


class UserTbl(db.Model):
    """User consisting of many Project."""

    __tablename__ = "users"

    user_id = Column(String(128), primary_key=True, index=True)
    password = Column(Text, nullable=False)
    name = Column(String(255), index=True)
    role = Column(String(255))
    is_active = Column(Boolean, default=False, nullable=False, index=True)
    description = Column(String(255))
    # Column Time
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __init__(self, user_id, password, name, role, is_active, description):
        self.user_id = user_id
        self.password = password
        self.name = name
        self.role = role
        self.is_active = is_active
        self.description = description

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'password': self.password,
            'name': self.name,
            'role': self.role,
            'is_active': self.is_active
        }
