# coding=UTF-8

from south.db import db
from django.db import models
from selvbetjening.core.members.models import *

class Migration:

    def forwards(self):
        # remove id
        db.delete_column('members_userprofile', 'id')

        # rename user_id to user_ptr_id
        #db.rename_column('members_userprofile', 'user_id', 'user_ptr_id')

    def backwards(self):
        "Write your backwards migration here"
