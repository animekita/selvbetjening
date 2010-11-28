from django.template.loader import render_to_string
from django.contrib.admin.helpers import AdminForm

from selvbetjening.core.members.processor_handlers import user_migration_processors
from selvbetjening.core.events.processor_handlers import change_selection_processors

import models

class UserMigrationProcessor(object):
    template_name = 'events/processors/user_migration.html'

    def __init__(self, request, old_user, new_user):
        self.request = request
        self.old_user = old_user
        self.new_user = new_user

        self.attend = models.Attend.objects.filter(user=self.old_user)
        self.overlapping_events = models.Event.objects.filter(attend__user=self.old_user)\
                                                      .filter(attend__user=self.new_user)

    def is_valid(self):
        return self.overlapping_events.count() == 0

    def render_function(self):
        models.Attend.objects.filter(user=self.old_user)

        return render_to_string(self.template_name,
                                {'count': self.attend.count(),
                                 'overlapping_events' : self.overlapping_events})


    def migrate(self):
        for attend in self.attend:
            attend.user = self.new_user
            attend.save()

user_migration_processors.register(UserMigrationProcessor)