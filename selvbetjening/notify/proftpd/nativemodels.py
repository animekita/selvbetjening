import sqlalchemy
from sqlalchemy.orm import mapper
from sqlalchemy.exceptions import OperationalError
import unicodedata

from django.core.exceptions import ImproperlyConfigured

_sessionmakers = {}
def _sessionmaker(native_db_id):
    global _sessionmakers

    if not _sessionmakers.has_key(native_db_id):
        import django.conf
        config = django.conf.settings.DATABASE_NATIVE.get(native_db_id)

        if config is None:
            raise ImproperlyConfigured('Native database not set correctly')

        if config['engine'] == 'mysql':
            url = '%(engine)s://%(username)s:%(password)s@%(host)s/%(name)s' % config
        elif config['engine'] == 'sqlite':
            url = '%(engine)s:///%(name)s' % config
        else:
            raise ImproperlyConfigured('Unsupported native database engine %s' % config['engine'])

        engine = sqlalchemy.create_engine(url, echo=False)
        _sessionmakers[native_db_id] = (engine, sqlalchemy.orm.sessionmaker(bind=engine, autoflush=True))
        sqlalchemy.convert_unicode=True

    return _sessionmakers[native_db_id]

class SessionWrapper(object):
    """
    Safe session which reconnects the engine to the database if necessary.
    """

    def __init__(self, native_db_id):
        self._native_db_id = native_db_id
        self._engine, self._sessionmaker = _sessionmaker(native_db_id)
        self._session = self._sessionmaker()

    def reset(self):
        global _sessionmakers
        del _sessionmakers[self._native_db_id]

        self._engine, self._sessionmaker = _sessionmaker(self._native_db_id)
        self._session = self._sessionmaker()

    def __getattr__(self, name):
        def safe_call(*args, **kwargs):
            orig_func = getattr(self._session, name)

            try:
                return orig_func(*args, **kwargs)
            except OperationalError:
                """ Raised if database connection has timed out """
                self.reset()

                new_func = getattr(self._session, name)
                new_func(*args, **kwargs)

        return safe_call

def get_session(native_db_id):
    return SessionWrapper(native_db_id)

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
    def __init__(self, name, gid, members):
        self.groupname = unicode(self.to_ascii(name))
        self.gid = gid
        self.members = unicode(members)

    def __repr__(self):
        return u"<NativeGroups(%s)" % self.groupname

    @classmethod
    def to_ascii(cls, string):
        return unicodedata.normalize('NFKD', string).encode('ascii','ignore')

    @property
    def id(self):
        return unicode(self.groupname)

    @classmethod
    def get_by_name(cls, session, groupname):
        try:
            result = session.query(cls).filter_by(groupname=unicode(cls.to_ascii(groupname))).all()
        except OperationalError:
            session.reset()
            result = session.query(cls).filter_by(groupname=unicode(cls.to_ascii(groupname))).all()

        object = None
        if len(result) > 0:
            object = result[0]

        return object

    @classmethod
    def get_all(cls, session):
        try:
            return session.query(cls).all()
        except OperationalError:
            session.reset()
            return session.query(cls).all()

    @classmethod
    def _initialize_sqlalchemy(cls):
        metadata = sqlalchemy.MetaData()
        table = sqlalchemy.Table('groups', metadata,
                                 sqlalchemy.Column('groupname', sqlalchemy.Unicode(255, assert_unicode=True), primary_key=True),
                                 sqlalchemy.Column('gid', sqlalchemy.Integer),
                                 sqlalchemy.Column('members', sqlalchemy.Unicode(255, assert_unicode=True))
                                 )

        mapper(cls, table)

NativeGroups._initialize_sqlalchemy()

class NativeUsers(NativeBase):
    def __init__(self, username, password, uid, gid, ftpdir, active=True):
        self.username = username
        self.passwd = password
        self.uid = uid
        self.gid = gid
        self.ftpdir = ftpdir
        self.shell = 'none'
        self.loginallowed = 1

        if active:
            self.active = 1
        else:
            self.active = 0

    @property
    def id(self):
        return self.user_id

    @classmethod
    def get_by_username(cls, session, username):
        try:
            result = session.query(cls).filter_by(username=username).all()
        except OperationalError:
            session.reset()
            result = session.query(cls).filter_by(username=username).all()

        object = None
        if len(result) > 0:
            object = result[0]

        return object

    @classmethod
    def _initialize_sqlalchemy(cls):
        metadata = sqlalchemy.MetaData()
        table = sqlalchemy.Table('users', metadata,
                                 sqlalchemy.Column('user_id', sqlalchemy.Integer, primary_key=True),
                                 sqlalchemy.Column('username', sqlalchemy.Unicode(255, assert_unicode=True)),
                                 sqlalchemy.Column('passwd', sqlalchemy.String(255)),
                                 sqlalchemy.Column('uid', sqlalchemy.Integer),
                                 sqlalchemy.Column('gid', sqlalchemy.Integer),
                                 sqlalchemy.Column('ftpdir', sqlalchemy.String(255)),
                                 sqlalchemy.Column('shell', sqlalchemy.String(255)),
                                 sqlalchemy.Column('loginallowed', sqlalchemy.SmallInteger),
                                 )

        mapper(cls, table)

NativeUsers._initialize_sqlalchemy()



