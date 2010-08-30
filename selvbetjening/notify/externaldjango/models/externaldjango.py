from django.contrib.auth.models import User, Group
from django.db import models

from native import GroupDjangoGroup

class DjangoGroupManager(models.Manager):
    def get(self, *args, **kwargs):
        """
        Adds support for the syntax
        DjangoGroup.objects.get(group=GROUP, database_id=DATABASE_ID)
        """

        if 'group' in kwargs and 'database_id' in kwargs:
            group = kwargs.pop('group')
            database_id = kwargs.pop('database_id')

            try:
                groupDjangoGroup = GroupDjangoGroup.objects.get(group=group,
                                                                database_id=database_id)
                return self.using(database_id).get(pk=groupDjangoGroup.djangogroup_id)
            except GroupDjangoGroup.DoesNotExist:
                raise DjangoGroup.DoesNotExist

        else:
            return super(DjangoGroupManager, self).get(*args, **kwargs)

class DjangoGroup(Group):
    objects = DjangoGroupManager()

    class Meta:
        managed = False
        proxy = True
        app_label = 'externaldjango'

class DjangoUser(User):
    class Meta:
        managed = False
        proxy = True
        app_label = 'externaldjango'

