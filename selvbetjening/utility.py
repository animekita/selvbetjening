class ProcessorHandler(object):
    def __init__(self, processors, *args, **kwargs):
        self._processors = [processor(*args, **kwargs) for processor in processors]

    def _call_all(self, function, *args, **kwargs):
        return_list = []

        for processor in self._processors:
            f = getattr(processor, function)
            return_list.append(f(*args, **kwargs))

        return return_list

    def _is_all_true(self, return_values):
        return reduce(lambda x, y : x and y, return_values, True)


class ProcessorRegistry(object):
    def __init__(self, handler):
        self.handler = handler
        self._registry = []

    def register(self, processor):
        self._registry.append(processor)

    def get_handler(self, *args, **kwargs):
        return self.handler(self._registry, *args, **kwargs)
