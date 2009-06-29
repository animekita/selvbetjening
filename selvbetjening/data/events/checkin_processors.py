from datetime import datetime

from django.template.loader import render_to_string
from django.contrib.admin.helpers import AdminForm

from models import Option

def options(request, user, event):
    options = user.option_set.filter(group__event=event)

    def selected_options_view():
        return render_to_string('events/checkin/options.html',
                                {'options' : options, })

    return (True, selected_options_view)