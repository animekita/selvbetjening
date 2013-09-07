from django.test import TransactionTestCase
from django.db import connections


class BaseNotifyTestCase(TransactionTestCase):
    def setUp(self):
        self.init_database('ext_database1')
        self.init_database('ext_database2')

    def tearDown(self):
        self.destroy_database('ext_database1')
        self.destroy_database('ext_database2')

    def check_databases(self, check_func):
        check_func('ext_database1')
        check_func('ext_database2')

    def init_database(self, database_id):
        self.register_notify(database_id)

        import os
        sqlpath = os.path.abspath(os.path.dirname(self._active_test_file))

        sqlfile = open(os.path.join(sqlpath, 'fixtures/nativedb.sql'), 'r')

        cursor = connections[database_id].cursor()

        cursor.executescript(sqlfile.read())

        sqlfile.close()

    def destroy_database(self, database_id):
        self.unregister_notify(database_id)

    def register_notify(self, database_id):
        raise NotImplementedError

    def unregister_notify(self, database_id):
        raise NotImplementedError