import sqlalchemy
from sqlalchemy.orm import mapper
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

_sessionmakers = {}
def _sessionmaker(native_db_id):
    global _sessionmakers

    if not _sessionmakers.has_key(native_db_id):
        config = settings.DATABASE_NATIVE.get(native_db_id)

        if config is None:
            raise ImproperlyConfigured('Native database not set correctly')

        if config['engine'] == 'mysql':
            url = '%(engine)s://%(username)s:%(password)s@%(host)s/%(name)s' % config
        elif config['engine'] == 'sqlite':
            url = '%(engine)s:///%(name)s' % config
        else:
            raise ImproperlyConfigured('Unsupported native database engine %s' % config['engine'])

        engine = sqlalchemy.create_engine(url, echo=True)
        _sessionmakers[native_db_id] = sqlalchemy.orm.sessionmaker(bind=engine, autoflush=True)

    return _sessionmakers[native_db_id]

def get_session(native_db_id):
    sessionmaker = _sessionmaker(native_db_id)
    return sessionmaker()

class NativeBase(object):

    @staticmethod
    def save(session, object):
        session.add(object)
        session.commit()

    @staticmethod
    def delete(session, object):
        session.delete(object)
        session.commit()

class NativeGroups(NativeBase):
    def __init__(self, name, description):
        self.gName = name
        self.gDescription = description

    def __repr__(self):
        return "<NativeGroups(%s, %s)" % (self.gName, self.gDescription)

    @property
    def id(self):
        return self.gID

    def _getname(self):
        return self.gName

    def _setname(self, value):
        self.gName = value

    name = property(_getname, _setname)

    @classmethod
    def get(cls, session, gID):
        result = session.query(cls).filter_by(gID=gID).all()

        object = None
        if len(result) > 0:
            object = result[0]

        return object

    @classmethod
    def get_by_name(cls, session, gName):
        result = session.query(cls).filter_by(gName=gName).all()

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
        self.uLastOnline = 0
        self.uLastLogin = 0
        self.uPreviousLogin = 0
        self.uPassword = ''
        self.uIsActive = 1
        self.uIsValidated = 1
        self.uIsFullRecord = 1
        self.uHasAvatar = 0
        self.uNumLogins = 0

    @property
    def id(self):
        return self.uID

    @classmethod
    def get_by_username(cls, session, uName):
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
    def get(cls, session, user_id, group_id):
        result = session.query(cls).filter_by(uID=user_id).filter_by(gID=group_id).all()

        object = None
        if len(result) > 0:
            object = result[0]

        return object

    @classmethod
    def remove_user(cls, session, user_id):
        result = session.query(cls).filter_by(uID=user_id).all()

        for object in result:
            session.delete(object)

        session.commit()

    @classmethod
    def remove_group(cls, session, group_id):
        result = session.query(cls).filter_by(gID=group_id).all()

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



