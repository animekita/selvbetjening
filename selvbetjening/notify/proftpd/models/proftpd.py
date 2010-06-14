from django.db import models

from native import GroupProftpdGroup

class ProftpdGroupManager(models.Manager):
    def get(self, *args, **kwargs):
        """
        Adds support for the syntax
        ProftpdGroup.objects.get(group=GROUP, database_id=DATABASE_ID)
        """

        if 'group' in kwargs and 'database_id' in kwargs:
            group = kwargs.pop('group')
            database_id = kwargs.pop('database_id')

            try:
                groupProftpdGroup = \
                    GroupProftpdGroup.objects.get(group=group,
                                                  database_id=database_id)

                return self.using(database_id).\
                            get(name=groupProftpdGroup.proftpdgroup_name)

            except GroupProftpdGroup.DoesNotExist:
                raise ProftpdGroup.DoesNotExist

        else:
            return super(ProftpdGroupManager, self).get(*args, **kwargs)

class ProftpdGroup(models.Model):
    name = models.TextField(primary_key=True, db_column='groupname')
    members = models.TextField(db_column='members')
    gid = models.IntegerField(db_column='gid')

    objects = ProftpdGroupManager()

    def add_member(self, member):
        if member == '':
            members = []
        else:
            members = self.members.split(',')

        members.append(member)

        self.members = ','.join(members)
        self.save()

    def remove_member(self, member):
        members = self.members.split(',')

        try:
            members.remove(member)
            self.members = ','.join(members)
            self.save()

        except ValueError:
            pass

    def is_member(self, member):
        return member in self.members.split(',')

    class Meta:
        db_table = 'groups'
        managed = False
        app_label = 'proftpd'

class ProftpdUser(models.Model):
    id = models.AutoField(primary_key=True, db_column='user_id')
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=50, db_column='passwd')
    uid = models.IntegerField()
    gid = models.IntegerField()
    ftpdir = models.CharField(max_length=255)
    shell = models.CharField(max_length=255, default='none')
    login_allowed = models.BooleanField(default=True, db_column='loginallowed')

    class Meta:
        db_table = 'users'
        managed = False
        app_label = 'proftpd'
