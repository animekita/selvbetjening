from django.conf.urls.defaults import *

from views import picture_edit, notification_edit

urlpatterns = patterns('',
    url(r'^billede/$', picture_edit,
        name='vanillaforum_editpicture'),

    url(r'^notification/$', notification_edit,
        name='vanillaforum_editnotifications'),
)