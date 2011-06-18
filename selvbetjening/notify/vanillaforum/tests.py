from django.contrib.auth.models import Group
from django.core.management.base import CommandError

from selvbetjening.core.events.tests import Database
from selvbetjening.notify.tests import BaseNotifyTestCase

from models import RemoteUser, RemoteUserAssociation, RemoteRole, \
     RemoteUserRole, GroupRemoteRole, registry, Settings
from management.commands import notify_vanillaforum_sync

class VanillaBaseTestCase(BaseNotifyTestCase):
    _active_test_file = __file__

    def register_notify(self, database_id):
        registry.register(database_id, {'database_id' : database_id,
                                        'default_role_id' : 3})

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


    def test_change_picture(self):
        """
        Change forum picture
        """

        user = Database.new_user()

        def action(database_id):
            remote_user = RemoteUser.objects.using(database_id).all()[0]
            self.assertEqual('', remote_user.photo_url)

        self.check_databases(action)

        import os
        CURRENTDIR = os.path.abspath(os.path.dirname(__file__))

        user_settings, created = Settings.objects.get_or_create(user=user)
        user_settings.picture = os.path.join(CURRENTDIR, 'test.png')
        user_settings.save()

        def action(database_id):
            remote_user = RemoteUser.objects.using(database_id).all()[0]
            self.assertNotEqual('', remote_user.photo_url)

        self.check_databases(action)

    def test_change_preferences(self):
        """
        Change user preferences
        """

        user = Database.new_user()

        def action(database_id):
            remote_user = RemoteUser.objects.using(database_id).all()[0]
            self.assertNotEqual(None, remote_user.preferences)
            self.assertFalse('NewDiscussion' in remote_user.preferences)

        self.check_databases(action)

        user_settings = Settings.objects.get(user=user)
        user_settings.notify_new_discussion_email = True
        user_settings.save()

        def action(database_id):
            remote_user = RemoteUser.objects.using(database_id).all()[0]
            self.assertTrue('NewDiscussion' in remote_user.preferences)

        self.check_databases(action)

    def test_groups(self):

        user = Database.new_user()
        group = Group.objects.create(name='test group')

        def action(database_id):
            remote_role = RemoteRole.objects.using(database_id)\
                                            .create(name='test role')

            GroupRemoteRole.objects.create(database_id=database_id,
                                           group=group,
                                           remote_role_id=remote_role.id)

        self.check_databases(action)

        group.user_set.add(user)

        def action(database_id):
            self.assertEqual(1, RemoteUserRole.objects.using(database_id).all().count())

        self.check_databases(action)



    def test_do_sync(self):
        user = Database.new_user()
        group = Group.objects.create(name='test group')

        def action(database_id):
            remote_role = RemoteRole.objects.using(database_id)\
                                            .create(name='test role')

            GroupRemoteRole.objects.create(database_id=database_id,
                                           group=group,
                                           remote_role_id=remote_role.id)

        self.check_databases(action)

        group.user_set.add(user)

        cmd = notify_vanillaforum_sync.Command()
        cmd.handle('sync')

        def action(database_id):
            self.assertEqual(1, RemoteUserRole.objects.using(database_id).all().count())

        self.check_databases(action)

