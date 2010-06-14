from django.db import models

from native import GroupC5Group

class C5User(models.Model):
    id = models.AutoField(primary_key=True, unique=True, db_column='uID')
    username = models.CharField(max_length=64, db_column='uName')
    email = models.CharField(max_length=64, db_column='uEmail')
    password = models.CharField(max_length=255, db_column='uPassword')

    is_active = models.BooleanField(db_column='uIsActive', blank=True, default=1)
    is_validated = models.BooleanField(db_column='uIsValidated', blank=True, default=-1)
    is_full_record = models.BooleanField(db_column='uIsFullRecord', blank=True, default=1)

    date_added = models.DateTimeField(db_column='uDateAdded')

    last_online = models.IntegerField(db_column='uLastOnline', blank=True, default=0)
    last_login = models.IntegerField(db_column='uLastLogin', blank=True, default=0)
    previous_login = models.IntegerField(db_column='uPreviousLogin', blank=True, default=0)
    num_logins = models.IntegerField(db_column='uNumLogins', blank=True, default=0)

    timezone = models.CharField(max_length=255, db_column='uTimezone', blank=True, null=True)
    has_avatar = models.BooleanField(db_column='uHasAvatar')

    objects = models.Manager()

    class Meta:
        db_table = 'Users'
        managed = False
        app_label = 'concrete5'

class C5GroupManager(models.Manager):
    def get(self, *args, **kwargs):
        """
        Adds support for the syntax
        C5Group.objects.get(group=GROUP, database_id=DATABASE_ID)
        """

        if 'group' in kwargs and 'database_id' in kwargs:
            group = kwargs.pop('group')
            database_id = kwargs.pop('database_id')

            try:
                groupC5Group = GroupC5Group.objects.get(group=group,
                                                        database_id=database_id)
                return self.using(database_id).get(pk=groupC5Group.c5group_id)
            except GroupC5Group.DoesNotExist:
                raise C5Group.DoesNotExist

        else:
            return super(C5GroupManager, self).get(*args, **kwargs)

class C5Group(models.Model):
    id = models.AutoField(primary_key=True, unique=True, db_column='gID')
    name = models.CharField(max_length=128, db_column='gName')
    description = models.CharField(max_length=255, db_column='gDescription')

    users = models.ManyToManyField(C5User, through='C5UserGroups')

    objects = C5GroupManager()

    class Meta:
        db_table = 'Groups'
        managed = False
        app_label = 'concrete5'

class C5UserGroups(models.Model):
    c5user = models.ForeignKey(C5User, primary_key=True, db_column='uID')
    c5group = models.ForeignKey(C5Group, db_column='gID')

    joined = models.DateTimeField(auto_now_add=True, db_column='ugEntered')
    relation_type = models.CharField(max_length=64, default=None, blank=True,
                                     null=True, db_column='type')

    class Meta:
        db_table = 'UserGroups'
        managed = False
        unique_together = ('c5user', 'c5group')
        app_label = 'concrete5'
