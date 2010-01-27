from django.template.loader import render_to_string

from selvbetjening.data.members.processor_handlers import user_migration_processors

import models

class UserMigrationProcessor(object):
    template_name = 'invoice/processors/user_migration.html'

    def __init__(self, request, old_user, new_user):
        self.request = request
        self.old_user = old_user
        self.new_user = new_user

        self.invoices = models.Invoice.objects.filter(user=self.old_user)

    def is_valid(self):
        return True

    def render_function(self):
        return render_to_string(self.template_name,
                                {'count': self.invoices.count()})


    def migrate(self):
        for invoice in self.invoices:
            invoice.user = self.new_user
            invoice.save()

user_migration_processors.register(UserMigrationProcessor)