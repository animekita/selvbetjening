from datetime import date

from django.db import models

from selvbetjening.eventmode.models import Eventmode as EventmodeModel

class EventmodeMiddleware():
    def process_request(self, request):
        request.eventmode = Eventmode(request)
        return None

class Eventmode():
    def __init__(self, request):
        self.request = request

    def activate(self, passphrase):
        if EventmodeModel.objects.check_passphrase(passphrase):
            self.request.session['eventmode_passphrase'] = passphrase
            return True
        else:
            return False

    def deactivate(self):
        if self.request.session.get('eventmode_passphrase', False):
            del(self.request.session['eventmode_passphrase'])

    def is_active(self):
        eventmode = self.get_model()

        if eventmode is not None and eventmode.is_valid():
            return True
        else:
            self.deactivate()
            return False

    def get_model(self):
        if self._get_passphrase():
            try:
                return EventmodeModel.objects.get(passphrase=self._get_passphrase())
            except EventmodeModel.DoesNotExist:
                pass

        return None

    def _get_passphrase(self, default=False):
        return self.request.session.get('eventmode_passphrase', default)
