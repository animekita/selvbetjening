from django.db import models
from django.conf import settings
from django.utils.importlib import import_module
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, load_backend
from django.contrib.auth.models import Group


class Service(models.Model):
    id = models.CharField(max_length=16, primary_key=True)
    visible_groups = models.ManyToManyField(Group)

    def __unicode__(self):
        return unicode(self.id)


def get_user_from_token(auth_token):
    engine = import_module(settings.SESSION_ENGINE)
    session = engine.SessionStore(auth_token)

    try:
        user_id = session[SESSION_KEY]
        backend_path = session[BACKEND_SESSION_KEY]

        backend = load_backend(backend_path)
        user = backend.get_user(user_id) or None
    except KeyError:
        return None

    return user


def get_new_user_session(user):
    engine = import_module(settings.SESSION_ENGINE)
    session = engine.SessionStore()

    session[SESSION_KEY] = user.id
    session[BACKEND_SESSION_KEY] = user.backend

    session.save(must_create=True)

    return session
