from datetime import timedelta, datetime

from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

import models

class ReservationForm(forms.Form):
    movie_title = forms.CharField(label=_('movie title'))
    description = forms.CharField(label=_('description'), required=False)
    startdate = forms.DateField(label=_('start date'), input_formats=('%d-%m-%Y', ))
    starttime = forms.TimeField(label=_('start time'), input_formats=['%H:%M', '%H.%M'],
                                help_text=_('provide the time in the format HH:MM, minutes must be given in whole quarters.'))
    enddate = forms.DateField(label=_('end date'), input_formats=('%d-%m-%Y', ))
    endtime = forms.TimeField(label=_('end time'), input_formats=['%H:%M', '%H.%M'],
                              help_text=_('provide the time in the format HH:MM, minutes must be given in whole quarters.'))

    def __init__(self, *args, **kwargs):
        self.cinema = kwargs['cinema']
        del(kwargs['cinema'])
        super(ReservationForm, self).__init__(*args, **kwargs)

        self.valid_dates = []
        self.dates = []
        time = self.cinema.starttime.date()
        while True:
            self.dates.append((time.strftime('%d-%m-%Y'), time.strftime('%d/%m - %Y')))
            self.valid_dates.append(time)

            time += timedelta(days=1)
            if time > self.cinema.endtime.date():
                break

        self.fields['startdate'].choices = self.dates
        self.fields['enddate'].choices = self.dates

    class Meta:
        layout = ((_('reservation'), (('movie_title', {'title' : True}), 'description')),
                  (_('time'), ('startdate', 'starttime', 'enddate', 'endtime'))
              )

    def clean_startdate(self):
        if not self.cleaned_data.get('startdate', '') in self.valid_dates:
            raise forms.ValidationError(_('Enter a valid date.'))

        return self.cleaned_data['startdate']

    def clean_enddate(self):
        if not self.cleaned_data['enddate'] in self.valid_dates:
            raise forms.ValidationError(_('Enter a valid date.'))

        return self.cleaned_data['enddate']

    def clean_starttime(self):
        if not (self.cleaned_data['starttime'].minute % 15) == 0:
            raise forms.ValidationError(_('Minutes must be dividable by 15'))

        return self.cleaned_data['starttime']

    def clean_endtime(self):
        if not (self.cleaned_data['endtime'].minute % 15) == 0:
            raise forms.ValidationError(_('Minutes must be dividable by 15'))

        return self.cleaned_data['endtime']

    def clean(self):
        if self.cleaned_data.has_key('startdate') and self.cleaned_data.has_key('starttime') and self.cleaned_data.has_key('enddate') and self.cleaned_data.has_key('endtime'):
            self.startdatetime = datetime.combine(self.cleaned_data['startdate'], self.cleaned_data['starttime'])
            self.enddatetime = datetime.combine(self.cleaned_data['enddate'], self.cleaned_data['endtime'])

            if not self.cinema.is_valid_reservation(self.startdatetime, self.enddatetime):
                raise forms.ValidationError(_('desired reservation interval not possible'))

        return self.cleaned_data

    def save(self, user):
        models.Reservation.objects.create(cinema=self.cinema,
                                          starttime=self.startdatetime,
                                          endtime=self.enddatetime,
                                          movie_title=self.cleaned_data['movie_title'],
                                          description=self.cleaned_data['description'],
                                          owner=user)
