from models import EventmodeMachine

class EventmodeMiddleware():
    def process_request(self, request):
        request.eventmode = Eventmode(request)
        return None

class Eventmode():
    def __init__(self, request):
        self.request = request

    def login(self, event, passphrase):
        eventmode = EventmodeMachine.objects.authenticate(event, passphrase)
        if eventmode is not None:
            self.request.session['eventmode_id'] = eventmode.id
            return True
        else:
            return False

    def logout(self):
        if self.request.session.get('eventmode_id', False):
            del(self.request.session['eventmode_id'])

    def is_authenticated(self):
        eventmode = self.model
        if eventmode is not None and eventmode.is_valid():
            return True
        else:
            return False

    @property
    def model(self):
        eventmode_id = self.request.session.get('eventmode_id', False)
        if eventmode_id:
            try:
                return EventmodeMachine.objects.get(id=eventmode_id)
            except EventmodeMachine.DoesNotExist:
                return None
