from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from selvbetjening.utility import ProcessorHandler, ProcessorRegistry

class ChangeSelectionHandler(ProcessorHandler):
    """
    Used when changing selections for an attendee through the admin interface.

    The processor needs to define the following methods.

    __init__(request, attendee) -- Current request object and an attendee object.

    view() -- Returns HTML displayed to the user, such as form elements  used to
    control the attendee selections.

    save() -- Called in order to save the changes.
    """

    def view(self):
        return ''.join(self._call_all('view'))

    def is_valid(self):
        return self._is_all_true(self._call_all('is_valid'))

    def save(self):
        self._call_all('save')

change_selection_processors = ProcessorRegistry(ChangeSelectionHandler)

class CheckinHandler(ProcessorHandler):
    """
    processor(request, attendee)
    view()
    """

    def view(self):
        return ''.join(self._call_all('view'))

checkin_processors = ProcessorRegistry(CheckinHandler)