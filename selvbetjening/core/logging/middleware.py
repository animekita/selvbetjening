
import threading


class SelvbetjeningGlobalRequestMiddleware(object):
    """
    Beware! dragons ahead if the thread local request is handled incorrectly.
    """

    thread_local_request = threading.local()

    def process_request(self, request):
        SelvbetjeningGlobalRequestMiddleware.thread_local_request.current = request

    def process_response(self, request, response):
        SelvbetjeningGlobalRequestMiddleware.thread_local_request.current = None
        return response

    def process_exception(self, request, exception):
        SelvbetjeningGlobalRequestMiddleware.thread_local_request.current = None
        return None


def get_thread_request():
    return getattr(SelvbetjeningGlobalRequestMiddleware.thread_local_request, 'current', None)
