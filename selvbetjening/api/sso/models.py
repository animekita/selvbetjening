from django.conf import settings
from django.utils.importlib import import_module
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, load_backend

def get_user_from_token(service, auth_token):
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
