class BaseListener(object):
    def __init__(self, listener_id, config):
        self._listener_id = listener_id
        self._config = config

        self._database_id = config['database_id']

    def handler(self, sender, **kwargs):
        raise NotImplemented

class BaseNotifyRegistry(object):
    def __init__(self):
        self._listeners = {}
        self._routing = []

    def register(self, listener_id, config):
        if not listener_id in self._listeners:
            self._listeners[listener_id] = []

        for signal, listener_class, sender in self._routing:
            listener = listener_class(listener_id, config)

            signal.connect(listener.handler, sender=sender)
            self._listeners[listener_id].append((signal, listener, sender))

    def unregister(self, listener_id):
        for signal, listener, sender in self._listeners[listener_id]:
            signal.disconnect(listener.handler, sender=sender)

        del self._listeners[listener_id]