from django.contrib.auth.models import Group
from django.core.management.base import CommandError

from selvbetjening.core.events.tests import Database
from selvbetjening.notify.tests import BaseNotifyTestCase

from models import RemoteUser, RemoteUserAssociation, registry

class VanillaBaseTestCase(BaseNotifyTestCase):
    _active_test_file = __file__

    def register_notify(self, database_id):
        registry.register(database_id, {'database_id' : database_id})

    def unregister_notify(self, database_id):
        registry.unregister(database_id)

class VanillaUserTestCase(VanillaBaseTestCase):
    def test_add_user(self):
        """
        Add new user

        Check that user is created in Vanilla and association is created
        """

        user1 = Database.new_user()
        user2 = Database.new_user()

        def action(database_id):
            self.assertEqual(2,
                             RemoteUser.objects.\
                                        using(database_id).\
                                        all().\
                                        count())

        self.check_databases(action)

    def test_remove_user(self):
        """
        Remove a user from Selvbetjening

        Check that the user association is removed in vanilla
        """

        user = Database.new_user()

        def action(database_id):
            user_count = RemoteUser.objects\
                                   .using(database_id)\
                                   .all()\
                                   .count()

            self.assertEqual(1, user_count)

        self.check_databases(action)

        user.delete()

        def action(database_id):
            user_count = RemoteUser.objects\
                                   .using(database_id)\
                                   .all()\
                                   .count()

            self.assertEqual(1, user_count)

            association_count = RemoteUserAssociation.objects\
                                                     .using(database_id)\
                                                     .all()\
                                                     .count()

            self.assertEqual(0, association_count)

        self.check_databases(action)

    def test_rename_user(self):
        """
        Rename user

        Check the username is changed in vanilla
        """

        user = Database.new_user()

        user.username = 'brand_new_username'
        user.save()

        def action(database_id):
            self.assertEqual(1,
                             RemoteUser.objects\
                                       .using(database_id)\
                                       .filter(username='brand_new_username')\
                                       .count())

        self.check_databases(action)
