from django.core import signals

user_changed_password = signals.Signal(providing_args=['user, password'])
user_changed_email = signals.Signal(providing_args=['user', 'email'])