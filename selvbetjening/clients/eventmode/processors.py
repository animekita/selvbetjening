from datetime import datetime

from django.template.loader import render_to_string
from django.contrib.admin.helpers import AdminForm

from selvbetjening.data.events.forms import OptionForms

def options(request, attendee):
    submit_allowed = False

    if request.method == 'POST':
        form = OptionForms(attendee.event, request.POST, attendee=attendee)
        if form.is_valid():
            submit_allowed = True
    else:
        form = OptionForms(attendee.event, attendee=attendee)

    admin_forms = []
    for option_form in form.forms:
        admin_forms.append(AdminForm(option_form,
                                     [(option_form.Meta.layout[0][0],
                                       {'fields': option_form.fields.keys()})],
                                     {}))

    def view_form():
        return render_to_string('eventmode/checkin/options.html',
                                {'adminforms' : admin_forms,
                                 'attendee' : attendee,
                                 })

    def save_form():
        form.save()

    return (submit_allowed, view_form, save_form)