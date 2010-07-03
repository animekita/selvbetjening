from django.conf import settings
from django.template import mark_safe

from selvbetjening.utility import ProcessorHandler, ProcessorRegistry

class ShowProfile(ProcessorHandler):
    """
    Each processor is given (request, user) in their constructor.

    View is called on the processor, expecting string output which is
    shown on the users profile.
    """

    def view(self):
        return mark_safe(''.join(self._call_all('view')))

profile_page_processors = ProcessorRegistry(ShowProfile)