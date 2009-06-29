from django.dispatch import Signal

user_created = Signal(providing_args=['instance', 'clear_text_password'])