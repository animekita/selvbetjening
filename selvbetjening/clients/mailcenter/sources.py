from django.core import signals
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save

sources = {'user_signed_up_to_event': (_('User signed up to event'), None, None),
           'user_joined_group': (_('User joined group'), None, None)}