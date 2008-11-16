from django.db import models
from django.contrib.auth.models import User

class Icon(models.Model):
    name = models.CharField(max_length=100)
    filename = models.FileField(upload_to='images/medals')

class Medal(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length=100)
    icon = models.ForeignKey(Icon)

