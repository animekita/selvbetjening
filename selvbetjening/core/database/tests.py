from django.test import TestCase
from django.db.models import Model

from dbrouter import DatabaseRouter

class TestModel(Model):
    pass

class TestModelExternal(Model):
    pass

class DatabaseRouterTestCase(TestCase):
    def test_allow_sync(self):
        dr = DatabaseRouter()

        DatabaseRouter.register_external_table(TestModelExternal, 'external')

        self.assertTrue(dr.allow_syncdb('default', TestModel))
        self.assertFalse(dr.allow_syncdb('external', TestModel))

        self.assertFalse(dr.allow_syncdb('default', TestModelExternal))
        self.assertTrue(dr.allow_syncdb('external', TestModelExternal))

    def test_allow_relation(self):
        dr = DatabaseRouter()

        DatabaseRouter.register_external_table(TestModelExternal, 'external')

        obj = TestModel()
        objExternal = TestModelExternal()

        self.assertTrue(dr.allow_relation(obj, obj))
        self.assertTrue(dr.allow_relation(objExternal, objExternal))
        self.assertFalse(dr.allow_relation(obj, objExternal))