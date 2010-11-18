# comparators

class Equals(object):
    name = 'is equals'

    @staticmethod
    def compare(field, argument):
        return field == argument

class IsGreaterThan(object):
    name = 'is greater than'

    def compare(field, argument):
        return field > argument

class IsLesserThan(object):
    name = 'is lesser than'

    def compare(field, argument):
        return field < argument

# list of types
# format (type_id, *comparators)

types = [('unicode', Equals),]

# list of parameters
# format param_id : (name, type, [*(field_id, name, type)])

parameters = {'user': ('User', None, [('username', 'Username', 'unicode'),
                                      ('age', 'Age', 'integer')])}


