from django.template.loader import render_to_string
from django.contrib.admin.helpers import AdminForm

from selvbetjening.data.events.forms import OptionForms
from selvbetjening.data.members.processor_handlers import user_migration_processors
from selvbetjening.data.events.processor_handlers import change_selection_processors

import models

class ChangeSelectionProcessor(object):
    def __init__(self, request, attendee):
        self.request = request
        self.attendee = attendee

        self.submit_allowed = False

        if request.method == 'POST':
            self.form = OptionForms(attendee.event, request.POST, attendee=attendee)
            if self.form.is_valid():
                self.submit_allowed = True
        else:
            self.form = OptionForms(attendee.event, attendee=attendee)

    def view(self):
        admin_forms = []
        for option_form in self.form.forms:
            admin_forms.append(AdminForm(option_form,
                                         [(option_form.Meta.layout[0][0],
                                           {'fields': option_form.fields.keys()})],
                                         {}))


        return render_to_string('admin/events/attend/checkin/options.html',
                                {'adminforms' : admin_forms,
                                 'attendee' : self.attendee,
                                 })

    def is_valid(self):
        return self.submit_allowed

    def save(self):
        self.form.save()

change_selection_processors.register(ChangeSelectionProcessor)

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