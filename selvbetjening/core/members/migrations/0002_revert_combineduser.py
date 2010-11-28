# coding=UTF-8

from south.db import db
from django.db import models
from selvbetjening.data.members.models import *

class Migration:

    def forwards(self):
        # rename user_ptr_id to user_id
        #db.rename_column('members_userprofile', 'user_ptr_id', 'user_id')
        pass

    def backwards(self):
        "Write your backwards migration here"
