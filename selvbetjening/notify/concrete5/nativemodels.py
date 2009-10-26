import sqlalchemy
from sqlalchemy.orm import mapper
from datetime import datetime

from django.conf import settings

def get_sessionmaker():
    url = '%(engine)s://%(username)s:%(password)s@%(host)s/%(name)s'
    db_settings = {'engine' : settings.C5_DATABASE_ENGINE,
                   'username' : settings.C5_DATABASE_USERNAME,
                   'password' : settings.C5_DATABASE_PASSWORD,
                   'host' : settings.C5_DATABASE_HOST,
                   'name' : settings.C5_DATABASE_NAME}

    engine = sqlalchemy.create_engine(url % db_settings, echo=True)
    return sqlalchemy.orm.sessionmaker(bind=engine, autoflush=True)

sessionmaker = get_sessionmaker()

_session = None
def _get_session():
    global _session

    if _session is None:
        _session = sessionmaker()

    return _session

def usingNativeDatabase(func):
    def decoractor(*args, **kwargs):
        global _session

        result = func(*args, **kwargs)

        if _session is not None:
            _session.commit()
            _session.close()
            _session = None

        return result

    return decoractor

class NativeBase(object):
    def save(self):
        session = _get_session()
        session.add(self)
        session.commit()

    def delete(self):
        session = _get_session()
        session.delete(self)
        session.commit()

class NativeGroups(NativeBase):
    def __init__(self, name, description):
        self.gName = name
        self.gDescription = description

    def __repr__(self):
        return "<Group(%s, %s)" % (self.name, self.description)

    @property
    def id(self):
        return self.gID

    def _getname(self):
        return self.gName

    def _setname(self, value):
        self.gName = value

    name = property(_getname, _setname)

    @classmethod
    def get(cls, gID):
        session = _get_session()
        result = session.query(cls).filter_by(gID=gID).all()

        object = None
        if len(result) > 0:
            object = result[0]

        return object

    @classmethod
    def _initialize_sqlalchemy(cls):
        metadata = sqlalchemy.MetaData()
        table = sqlalchemy.Table('Groups', metadata,
                                 sqlalchemy.Column('gID', sqlalchemy.Integer, primary_key=True),
                                 sqlalchemy.Column('gName', sqlalchemy.String(128)),
                                 sqlalchemy.Column('gDescription', sqlalchemy.String(255))
                                 )

        mapper(cls, table)

NativeGroups._initialize_sqlalchemy()

class NativeUsers(NativeBase):
    def __init__(self, name, email, created_date):
        self.uName = name
        self.uEmail = email
        self.uDateAdded = created_date
        self.uPassword = ''
        self.uIsActive = 1

    @property
    def id(self):
        return self.uID

    @classmethod
    def get_by_username(cls, uName):
        session = _get_session()
        result = session.query(cls).filter_by(uName=uName).all()

        object = None
        if len(result) > 0:
            object = result[0]

        return object


    @classmethod
    def _initialize_sqlalchemy(cls):
        metadata = sqlalchemy.MetaData()
        table = sqlalchemy.Table('Users', metadata,
                                 sqlalchemy.Column('uID', sqlalchemy.Integer, primary_key=True),
                                 sqlalchemy.Column('uName', sqlalchemy.String(64)),
                                 sqlalchemy.Column('uEmail', sqlalchemy.String(64)),
                                 sqlalchemy.Column('uPassword', sqlalchemy.String(255)),
                                 sqlalchemy.Column('uIsActive', sqlalchemy.String(1)),
                                 sqlalchemy.Column('uIsValidated', sqlalchemy.SmallInteger),
                                 sqlalchemy.Column('uIsFullRecord', sqlalchemy.SmallInteger),
                                 sqlalchemy.Column('uDateAdded', sqlalchemy.DateTime),
                                 sqlalchemy.Column('uHasAvatar', sqlalchemy.SmallInteger),
                                 sqlalchemy.Column('uLastOnline', sqlalchemy.Integer),
                                 sqlalchemy.Column('uLastLogin', sqlalchemy.Integer),
                                 sqlalchemy.Column('uPreviousLogin', sqlalchemy.Integer),
                                 sqlalchemy.Column('uNumLogins', sqlalchemy.Integer),
                                 sqlalchemy.Column('uTimezone', sqlalchemy.String(255)),
                                 )

        mapper(cls, table)

NativeUsers._initialize_sqlalchemy()

class NativeUserGroups(NativeBase):
    def __init__(self, user_id, group_id):
        self.uID = user_id
        self.gID = group_id
        self.ugEntered = datetime.today()


    @classmethod
    def get(cls, user_id, group_id):
        session = _get_session()
        result = session.query(cls).filter_by(uID=user_id).filter_by(gID=group_id).all()

        object = None
        if len(result) > 0:
            object = result[0]

        return object

    @classmethod
    def remove_user(cls, user_id):
        session = _get_session()
        result = session.query(cls).filter_by(uID=user_id).all()

        for object in result:
            session.delete(object)

        session.commit()

    @classmethod
    def _initialize_sqlalchemy(cls):
        metadata = sqlalchemy.MetaData()
        table = sqlalchemy.Table('UserGroups', metadata,
                                 sqlalchemy.Column('uID', sqlalchemy.Integer, primary_key=True),
                                 sqlalchemy.Column('gID', sqlalchemy.Integer, primary_key=True),
                                 sqlalchemy.Column('ugEntered', sqlalchemy.DateTime),
                                 sqlalchemy.Column('type', sqlalchemy.String(64)),
                                 )

        mapper(cls, table)

NativeUserGroups._initialize_sqlalchemy()



