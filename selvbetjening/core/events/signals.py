
from django.db.models.signals import Signal

request_attendee_pks_signal = Signal(providing_args=['attendee'])
find_attendee_signal = Signal(providing_args=['pk'])

attendee_updated_signal = Signal(providing_args=['attendee'])