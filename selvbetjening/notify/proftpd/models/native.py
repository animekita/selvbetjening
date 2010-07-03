from django.db import models
from django.contrib.auth.models import Group, User

class GroupProftpdGroup(models.Model):
    group = models.ForeignKey(Group)
    proftpdgroup_name = models.CharField(max_length=255)
    database_id = models.CharField(max_length=32)

    class Meta:
        unique_together = ('proftpdgroup_name', 'database_id')
        app_label = 'proftpd'

class CompatiblePassword(models.Model):
    user = models.OneToOneField(User)
    password = models.CharField(max_length=255)

    class Meta:
        app_label = 'proftpd'