from django.db import models

class RemoteUser(models.Model):

    id = models.AutoField(primary_key=True, unique=True, db_column='UserID')
    username = models.CharField(max_length=20, unique=True, db_column='Name')

    password = models.CharField(max_length=50, db_column='Password')
    email = models.CharField(max_length=200, db_column='Email')

    registration_date = models.DateTimeField(auto_now_add=True, db_column='DateInserted')
    first_visit_date = models.DateTimeField(default=None, db_column='DateFirstVisit')

    class Meta:
        db_table = 'GDN_User'
        managed = False
        app_label = 'vanillaforum'

class RemoteUserAssociationManager(models.Manager):

    def create(self, *args, **kwargs):
        kwargs['provider'] = 'selvbetjeningsso'

        return super(RemoteUserAssociation, self).create(*args, **kwargs)

    def get_query_set(self):
        return super(RemoteUserAssociationManager, self).get_query_set().filter(provider='selvbetjeningsso')

class RemoteUserAssociation(models.Model):

    selv_user_id = models.CharField(max_length=255, primary_key=True, db_column='ForeignUserKey')
    remote_user_id = models.IntegerField(db_column='UserID')

    provider = models.CharField(max_length=64, primary_key=True, default='selvbetjeningsso', db_column='ProviderKey')

    objects = RemoteUserAssociationManager()

    class Meta:
        db_table = 'GDN_UserAuthentication'
        managed = False
        app_label = 'vanillaforum'