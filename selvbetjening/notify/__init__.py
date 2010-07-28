class BaseListener(object):
    def __init__(self, listener_id, config):
        self._listener_id = listener_id
        self._config = config

        self._database_id = config['database_id']

    def handler(self, sender, **kwargs):
        raise NotImplemented

class BaseNotifyRegistry(object):
    def __init__(self):
        self._registry = {}
        self.listeners = {}
        self._routing = []

    def register(self, listener_id, config):
        if listener_id in self._registry:
            raise RuntimeError('listener with given id already registered')

        self._registry[listener_id] = []
        self.listeners[listener_id] = config

        for signal, listener_class, sender in self._routing:
            listener = listener_class(listener_id, config)

            kwargs = {}
            if sender is not None:
                kwargs['sender'] = sender

            signal.connect(listener.handler, **kwargs)
            self._registry[listener_id].append((signal, listener, sender))

    def unregister(self, listener_id):
        for signal, listener, sender in self._registry[listener_id]:
            signal.disconnect(listener.handler, sender=sender)

        del self._registry[listener_id]