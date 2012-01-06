from django.conf import settings
from django.utils.safestring import mark_safe

from selvbetjening.utility import ProcessorHandler, ProcessorRegistry

class SignupHandler(ProcessorHandler):
    """
    Each processor is given (request, user, event) in their constructor.
    """

    def is_valid(self):
        valid = True
        for result in self._call_all('is_valid'):
            valid = valid and result

        return valid

    def view(self):
        return mark_safe(''.join(self._call_all('view')))

    def save(self, attendee):
        self._call_all('save', attendee)

signup_processors = ProcessorRegistry(SignupHandler)

class ChangeHandler(ProcessorHandler):
    """
    __init__(request, user, event)
    """

    def is_valid(self):
        valid = True
        for result in self._call_all('is_valid'):
            valid = valid and result

        return valid

    def view(self):
        return ''.join(self._call_all('view'))

    def save(self):
        self._call_all('save')
        
    def postsave(self):
        self._call_all('postsave')

change_processors = ProcessorRegistry(ChangeHandler)