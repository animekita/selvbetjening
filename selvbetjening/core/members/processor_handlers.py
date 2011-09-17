from django.conf import settings
from django.utils.safestring import mark_safe

from selvbetjening.utility import ProcessorHandler, ProcessorRegistry

class UserMigrationHandler(ProcessorHandler):
    """
    Called when migrating user data from old_user to new_user.

    First, a confirmation page is shown to the user, showing possible
    output from the render_function method. If the user confirms, the
    is_valid() method is called on all of the processors.

    If all of the  processors returns True, the user is migrated and
    the migrate() method is called.

    If one of the processors' is_valid() method returns False, the
    migration is blocked and render_function() is called again on
    all processors in order to shown possible error messages.

    """

    def is_valid(self):
        return self._is_all_true(self._call_all('is_valid'))

    def render_function(self):
        return mark_safe(''.join(self._call_all('render_function')))

    def migrate(self):
        self._call_all('migrate')

user_migration_processors = ProcessorRegistry(UserMigrationHandler)
