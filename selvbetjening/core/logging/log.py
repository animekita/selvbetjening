
import logging

from selvbetjening.core.logging.middleware import get_thread_request


class DBHandler(logging.Handler):

    def __init__(self, *args, **kwargs):
        super(DBHandler, self).__init__(*args, **kwargs)
        self._log_model = None

    def emit(self, record):

        if self._log_model is None:
            # Cache the import for performance
            from models import Log
            self._log_model = Log

        request = get_thread_request()

        if request is None:
            request_user = None
            request_ip = None

        else:
            request_user = None if request.user.is_anonymous() else request.user
            request_ip = \
                request.META.get('HTTP_X_FORWARDED_FOR', None) or \
                request.META.get('Client-IP', None) or \
                request.META.get('REMOTE_ADDR', None)

        self._log_model.objects.create(
            request_user=request_user,
            request_ip=request_ip,
            source=record.name,
            level=record.levelname,
            msg=record.getMessage(),
            related_attendee=getattr(record, 'related_attendee', None),
            related_user=getattr(record, 'related_user', None),
            related_email=getattr(record, 'related_email', None)
        )
