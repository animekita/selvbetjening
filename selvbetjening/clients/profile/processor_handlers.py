from django.conf import settings

from selvbetjening.utility import ProcessorHandler

"""
processor(user)
view_func()
save_func()
"""
viewprofile = ProcessorHandler(settings.PROFILE_VIEW_PROCESSORS)