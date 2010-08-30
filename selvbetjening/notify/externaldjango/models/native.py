from django.db import models
from django.contrib.auth.models import Group, User

class GroupDjangoGroup(models.Model):
    group = models.ForeignKey(Group)
    djangogroup_id = models.PositiveIntegerField()
    database_id = models.CharField(max_length=32)

    objects = models.Manager()

    class Meta:
        unique_together = ('djangogroup_id', 'database_id')
        app_label = 'externaldjango'