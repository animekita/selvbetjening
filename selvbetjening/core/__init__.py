class ObjectWrapper(object):
    def __init__(self, obj):
        self.obj = obj

    def __getattribute__(self, name):
        try:
            return super(ObjectWrapper, self).__getattribute__(name)
        except AttributeError:
            return self.obj.__getattribute__(name)