class DatabaseRouter(object):
    _external_tables = {}

    @classmethod
    def register_external_table(cls, model, database_name):
        databases = cls._external_tables.get(model, [])
        databases.append(database_name)

        cls._external_tables[model] = databases

    def allow_relation(self, obj1, obj2, **hints):
        if obj1.__class__ in self._external_tables:
            if obj2.__class__ in self._external_tables:
                model1 = self._external_tables[obj1.__class__]
                model2 = self._external_tables[obj2.__class__]

                return len(set(model1).intersection(set(model2))) > 0
            else:
                return False # only obj1 is external table

        if obj2.__class__ in self._external_tables:
            return False # only obj2 is external table

        return True

    def db_for_write(self, model, **hints):
        return False

    def db_for_read(self, model, **hints):
        return False

    def allow_syncdb(self, db, model):

        if model in self._external_tables:
            return db in self._external_tables[model]

        return db == 'default' or model._meta.app_label in ['contenttypes', ]

