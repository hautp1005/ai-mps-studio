from sqlalchemy import Column, DateTime, ForeignKey, Boolean, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, desc

from . import db


# table for relationship many to many
# user_project = Table('user_project', db.metadata,
#                      Column('user_id', String(128), ForeignKey('users.user_id'), primary_key=True),
#                      Column('prj_id', String(128), ForeignKey('projects.prj_id'), primary_key=True)
#                      )


# Users

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


# Projects

def get_all_project():
    projects = ProjectTbl.query.order_by(desc(ProjectTbl.is_active)).all()
    return projects


def get_all_active_project():
    projects = ProjectTbl.query.filter_by(is_active=True).order_by(desc(ProjectTbl.is_active)).all()
    return projects


def get_all_active_project_user(user_name_logged):
    own_prj_list = []
    projects = ProjectTbl.query.filter_by(is_active=True).order_by(desc(ProjectTbl.is_active)).all()
    for i in projects:
        m = i.member
        for k, v in m.items():
            if user_name_logged in v:
                own_prj_list += [i.prj_name]
    return own_prj_list


def add_project(prj_id, prj_name, is_active, member):
    db.session.add(ProjectTbl(prj_id=prj_id, prj_name=prj_name, is_active=is_active, member=member))
    db.session.commit()


def get_project_member(prj_id):
    projects_member = ProjectTbl.query.filter_by(prj_id=prj_id).all()
    prj_member = {}
    member_list = []
    for prj in projects_member:
        prj_member = prj.member
    for key, value in prj_member.items():
        member_list = value
    return member_list


def is_exist_prj_id(prj_id):
    is_exists = db.session.query(ProjectTbl).filter(ProjectTbl.prj_id == prj_id).first()
    return is_exists


def is_exist_prj_name(prj_name):
    is_exists = db.session.query(ProjectTbl).filter(ProjectTbl.prj_name == prj_name).first()
    return is_exists


def get_total_project(*args):
    if args:
        total_prj = ProjectTbl.query.filter_by(is_active=True).count()
    else:
        total_prj = ProjectTbl.query.count()
    return total_prj


# Devices

def get_all_device():
    devices = DeviceTbl.query.order_by(desc(DeviceTbl.is_active)).all()
    return devices


def get_device_info(device_id):
    query_device = db.session.query(DeviceTbl).filter(DeviceTbl.device_id == device_id)
    return query_device


def get_list_all_device_project(prj_id):
    own_device_project_list = []
    query_project = db.session.query(ProjectTbl.prj_id,
                                     ProjectTbl.prj_name,
                                     ProjectTbl.member,
                                     DeviceTbl.device_id,
                                     DeviceTbl.device_name,
                                     DeviceTbl.device_status) \
        .join(ProjectTbl, DeviceTbl.prj_id == ProjectTbl.prj_id) \
        .filter_by(prj_id=prj_id) \
        .filter(DeviceTbl.device_status) \
        .filter(DeviceTbl.is_active)
    for device in query_project.all():
        own_device_project_list += [device.device_name]

    return own_device_project_list


def add_device(device_id, device_name, device_platform_name, device_status, is_active, prj_id):
    db.session.add(DeviceTbl(device_id=device_id, device_name=device_name, device_platform_name=device_platform_name,
                             device_status=device_status, is_active=is_active, prj_id=prj_id))
    db.session.commit()


def is_exists_device_id(device_id):
    is_exists = db.session.query(DeviceTbl).filter(DeviceTbl.device_id == device_id).first()
    return is_exists


def is_exists_device_name(device_name):
    is_exists = db.session.query(DeviceTbl).filter(DeviceTbl.device_name == device_name).first()
    return is_exists


def get_total_device(*args):
    if args:
        total_device = DeviceTbl.query.filter_by(is_active=True).count()
    else:
        total_device = DeviceTbl.query.count()
    return total_device


def update_device(device_id, data_update):
    db.session.query(DeviceTbl).filter_by(device_id=device_id).update(data_update)
    db.session.commit()


# Testcases
def get_all_testcase():
    testcases = TestCaseTbl.query.order_by(desc(TestCaseTbl.is_active)).all()
    return testcases


def get_testcase(prj_id):
    testcases = db.session.query(TestCaseTbl).filter(TestCaseTbl.prj_id == prj_id).first()
    return testcases


def get_testcase_project(prj_name):
    own_testcase_project_list = []
    query_project = db.session.query(ProjectTbl.prj_id,
                                     ProjectTbl.prj_name,
                                     ProjectTbl.member,
                                     TestCaseTbl.tc_id,
                                     TestCaseTbl.tc_name) \
        .join(ProjectTbl, TestCaseTbl.prj_id == ProjectTbl.prj_id) \
        .filter_by(prj_name=prj_name) \
        .filter(TestCaseTbl.is_active)
    for tc in query_project.all():
        own_testcase_project_list += [tc.tc_name]

    return own_testcase_project_list


def add_testcase(tc_id, tc_name, description, is_active, prj_id):
    db.session.add(
        TestCaseTbl(tc_id=tc_id, tc_name=tc_name, description=description, is_active=is_active, prj_id=prj_id))
    db.session.commit()


def is_exists_tc_id(tc_id):
    is_exists = db.session.query(TestCaseTbl).filter(TestCaseTbl.tc_id == tc_id).first()
    return is_exists


def is_exists_tc_name(tc_name):
    is_exists = db.session.query(TestCaseTbl).filter(TestCaseTbl.tc_name == tc_name).first()
    return is_exists


def get_total_testcase(*args):
    if args:
        total_testcase = TestCaseTbl.query.filter_by(is_active=True).count()
    else:
        total_testcase = TestCaseTbl.query.count()
    return total_testcase


def update_testcase(tc_id, data_update):
    db.session.query(TestCaseTbl).filter_by(tc_id=tc_id).update(data_update)
    db.session.commit()


def add_logs(user_id, logs, action):
    db.session.add(LogTbl(user_id=str(user_id), logs=logs, action=str(action)))
    db.session.commit()


def get_all_logs():
    logs = LogTbl.query.order_by(desc(LogTbl.created_at)).all()
    return logs


def get_total_logs():
    total_log = LogTbl.query.count()
    return total_log


# Running
def get_all_running():
    query_running = db.session.query(RunningTbl.user_id,
                                     RunningTbl.status,
                                     RunningTbl.tc_condition,
                                     ProjectTbl.prj_name,
                                     TestCaseTbl.tc_name,
                                     DeviceTbl.device_name) \
        .outerjoin(ProjectTbl, RunningTbl.prj_id == ProjectTbl.prj_id) \
        .outerjoin(TestCaseTbl, RunningTbl.tc_id == TestCaseTbl.tc_id) \
        .outerjoin(DeviceTbl, RunningTbl.device_id == DeviceTbl.device_id)
    return query_running


def get_running_info(status):
    query_running = db.session.query(RunningTbl).filter(RunningTbl.status == status)
    return query_running


def get_all_user_running(user_id):
    query_running = db.session.query(RunningTbl.user_id,
                                     RunningTbl.status,
                                     RunningTbl.tc_condition,
                                     ProjectTbl.prj_name,
                                     TestCaseTbl.tc_name,
                                     TestCaseTbl.description,
                                     DeviceTbl.device_name) \
        .outerjoin(ProjectTbl, RunningTbl.prj_id == ProjectTbl.prj_id) \
        .outerjoin(TestCaseTbl, RunningTbl.tc_id == TestCaseTbl.tc_id) \
        .outerjoin(DeviceTbl, RunningTbl.device_id == DeviceTbl.device_id) \
        .filter(RunningTbl.user_id == user_id)
    return query_running


def get_project_testcase():
    query_project = db.session.query(ProjectTbl.prj_id,
                                     ProjectTbl.prj_name,
                                     ProjectTbl.member,
                                     TestCaseTbl.tc_id,
                                     TestCaseTbl.tc_name) \
        .join(ProjectTbl, TestCaseTbl.prj_id == ProjectTbl.prj_id)
    return query_project


def get_project_device():
    query_project = db.session.query(ProjectTbl.prj_id,
                                     ProjectTbl.prj_name,
                                     ProjectTbl.member,
                                     DeviceTbl.device_id,
                                     DeviceTbl.device_name) \
        .join(DeviceTbl, ProjectTbl.prj_id == DeviceTbl.prj_id)
    return query_project


def get_total_running():
    total_running = RunningTbl.query.count()
    return total_running


def get_total_testcase_running():
    total_running = RunningTbl.query.filter_by(status='Running').count()
    return total_running


def add_running(user_id, prj_id, tc_id, device_id, status, tc_condition):
    db.session.add(RunningTbl(user_id=user_id, prj_id=prj_id,
                              tc_id=tc_id,
                              device_id=device_id,
                              status=status,
                              tc_condition=tc_condition))
    db.session.commit()


def add_cond(cond_name, cond_group, is_active):
    db.session.add(ConditionTbl(cond_name=cond_name, cond_group=cond_group, is_active=is_active))
    db.session.commit()


def update_cond(cond_id, data_update):
    db.session.query(ConditionTbl).filter_by(id=cond_id).update(data_update)
    db.session.commit()


def is_exist_cond_name(cond_name):
    is_exists = db.session.query(ConditionTbl).filter(ConditionTbl.cond_name == cond_name).first()
    return is_exists


def get_all_cond():
    conditions = ConditionTbl.query.all()
    return conditions


def get_all_active_cond(cond_group):
    conditions = ConditionTbl.query.filter_by(is_active=True).filter(ConditionTbl.cond_group == cond_group).order_by(
        desc(ConditionTbl.is_active)).all()
    return conditions


def get_total_cond():
    total_cond = ConditionTbl.query.filter_by(is_active=True).count()
    return total_cond


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

    # Relationship many to many
    running = relationship("RunningTbl", backref="users")

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


class ProjectTbl(db.Model):
    """Project consisting of many users."""
    """Project consisting of many testcase."""
    """Project consisting of many devices."""

    __tablename__ = "projects"

    prj_id = Column(String(128), primary_key=True, index=True)
    prj_name = Column(String(128), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, nullable=False)
    member = Column(JSON)

    # Column Time
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationship
    testcases = relationship("TestCaseTbl", backref="projects")
    devices = relationship("DeviceTbl", backref="projects")
    running = relationship("RunningTbl", backref="projects")

    def __init__(self, prj_id, prj_name, is_active, member):
        self.prj_id = prj_id
        self.prj_name = prj_name
        self.is_active = is_active
        self.member = member


class TestCaseTbl(db.Model):
    """Individual testcase belonging to a Project."""
    """Testcase consisting of many devices."""

    __tablename__ = "testcases"

    tc_id = Column(String(128), primary_key=True, nullable=False, index=True)
    tc_name = Column(String(128), unique=True, nullable=False, index=True)
    description = Column(String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)

    # FK added
    prj_id = Column(String(128), ForeignKey("projects.prj_id"), nullable=False)

    # Column Time
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationship
    running = relationship("RunningTbl", backref="testcases")

    def __init__(self, tc_id, tc_name, description, is_active, prj_id):
        self.tc_id = tc_id
        self.tc_name = tc_name
        self.description = description
        self.is_active = is_active
        self.prj_id = prj_id

    def to_dict(self):
        return {
            'tc_id': self.tc_id,
            'tc_name': self.tc_name,
            'description': self.description,
            'is_active': self.is_active,
            'prj_id': self.prj_id
        }


class DeviceTbl(db.Model):
    """Individual device belonging to a Testcase."""

    __tablename__ = "devices"

    device_id = Column(String(128), primary_key=True, nullable=False, index=True)
    device_name = Column(String(128), unique=True, nullable=False, index=True)
    device_platform_name = Column(String(128), index=True)
    device_status = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)

    # Column Time
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # FK added
    prj_id = Column(String(128), ForeignKey("projects.prj_id"), nullable=False)

    # Relationship
    running = relationship("RunningTbl", backref="devices")

    def __init__(self, device_id, device_name, device_platform_name, device_status, is_active, prj_id):
        self.device_id = device_id
        self.device_name = device_name
        self.device_platform_name = device_platform_name
        self.device_status = device_status
        self.is_active = is_active
        self.prj_id = prj_id

    def to_dict(self):
        return {
            'device_id': self.device_id,
            'device_name': self.device_name,
            'device_platform_name': self.device_platform_name,
            'device_status': self.device_status,
            'is_active': self.is_active,
            'prj_id': self.prj_id
        }


class RunningTbl(db.Model):
    """Individual device belonging to a Testcase."""

    __tablename__ = "running"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(String(128), index=True)
    tc_condition = db.Column(String(1000), index=True)

    # FK added
    user_id = Column(String(128), ForeignKey("users.user_id"), nullable=False)
    prj_id = Column(String(128), ForeignKey("projects.prj_id"), nullable=False)
    tc_id = Column(String(128), ForeignKey("testcases.tc_id"), nullable=False)
    device_id = Column(String(128), ForeignKey("devices.device_id"), nullable=False)

    # Column Time
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __init__(self, user_id, prj_id, tc_id, device_id, status, tc_condition):
        self.user_id = user_id
        self.prj_id = prj_id
        self.tc_id = tc_id
        self.device_id = device_id
        self.status = status
        self.tc_condition = tc_condition

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'prj_id': self.prj_id,
            'tc_id': self.tc_id,
            'device_id': self.device_id,
            'status': self.status,
            'tc_condition': self.tc_condition
        }


class LogTbl(db.Model):
    __tablename__ = "action_logs"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(String(128), index=True)
    logs = Column(JSON)
    action = Column(String(255))
    # Column Time
    created_at = Column(DateTime, server_default=func.now())

    def __init__(self, user_id, logs, action):
        self.user_id = user_id
        self.logs = logs
        self.action = action


class ConditionTbl(db.Model):
    __tablename__ = "conditions"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cond_name = Column(String(1000), unique=True, nullable=False, index=True)
    cond_group = db.Column(String(1000), nullable=False, index=True)
    is_active = Column(Boolean, default=False, nullable=False, index=True)
    # Column Time
    created_at = Column(DateTime, server_default=func.now())

    def __init__(self, cond_name, cond_group, is_active):
        self.cond_name = cond_name
        self.cond_group = cond_group
        self.is_active = is_active

    def to_dict(self):
        return {
            'cond_name': self.cond_name,
            'cond_group': self.cond_group,
            'is_active': self.is_active
        }
