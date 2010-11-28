from django.conf import settings
from django.template import mark_safe

from selvbetjening.utility import ProcessorHandler, ProcessorRegistry

class ShowProfile(ProcessorHandler):
    """
    Each processor is given (request, user) in their constructor.

    View is called on the processor, expecting string output which is
    shown on the users profile.
    """

    def view(self, own_profile):
        return mark_safe(''.join(self._call_all('view', own_profile)))

profile_page_processors = ProcessorRegistry(ShowProfile)

class ExtendedPrivacy(ProcessorHandler):
    """
    Each processor is given (user) in their constructor.
    """

    def get_privacy_options(self):
        """
        Returns a list of tuples (key, name, value)
        representing the current privacy setting.
        """
        all_options = []
        for options in self._call_all('get_privacy_options'):
            all_options.extend(options)

        return all_options

    def save_privacy_options(self, options):
        """
        Gets a list of tuples which have been changed and now needs to be updated.
        """

        self._call_all('save_privacy_options', options)

extended_privacy_processors = ProcessorRegistry(ExtendedPrivacy)