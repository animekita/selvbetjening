from django.db import models
from django.contrib.auth.models import Group, User

class GroupC5Group(models.Model):
    group = models.ForeignKey(Group)
    c5group_id = models.PositiveIntegerField(db_column='c5group_id')
    database_id = models.CharField(max_length=32)

    objects = models.Manager()

    class Meta:
        db_table = 'GroupC5Group'
        unique_together = ('c5group_id', 'database_id')
        app_label = 'concrete5'