"""
    sadmin views

    Insert a view for each page you want to add.

    IMPORTANT: Prefix all views by @sadmin_prerequisites, this adds authentication and authorization to the views.

    You should add the following items to the view context for all rendered pages:

    sadmin2_menu_main_active: The ID of the currently active page in the main menu.
    sadmin2_breadcrumb_active: The ID of the current breadcrumb sequence you want to use.
    sadmin2_menu_tab: The tab-menu you want rendered
    sadmin2_menu_tab_active: The ID of the item in the tab-menu you want highlighted.

    search_url (optinal): If provided, a searchbox will be rendered and results returned by <search_url> will be
                          injected into #searchresult.

"""

from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect

from selvbetjening.core.events.models import Event, payment_registered_source, Payment

from selvbetjening.sadmin2.forms import EventForm, RegisterPaymentForm
from selvbetjening.sadmin2.decorators import sadmin_prerequisites
from selvbetjening.sadmin2 import menu

from generic import search_view


@sadmin_prerequisites
def event_list(request):

    queryset = Event.objects.all()
    columns = ('title',)

    context = {
        'sadmin2_menu_main_active': 'events',
        'sadmin2_breadcrumbs_active': 'events',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_events,
        'sadmin2_menu_tab_active': 'events',
    }

    return search_view(request,
                       queryset,
                       'sadmin2/events/list.html',
                       'sadmin2/events/list_inner.html',
                       search_columns=columns,
                       context=context)


@sadmin_prerequisites
def event_list_ajax(self, request, extra_context=None):
    response = self.changelist_view(request, extra_context)

    start = response.content.rfind('<form')
    stop = response.content.rfind('</form>') + 7
    response.content = response.content[start:stop]

    return response


@sadmin_prerequisites
def event_create(request):

    if request.method == 'POST':
        form = EventForm(request.POST)

        if form.is_valid():
            event = form.save()
            messages.add_message(request, messages.SUCCESS, _('Event created'))
            return HttpResponseRedirect(reverse('sadmin2:event_attendees', kwargs={'event_pk': event.pk}))

    else:
        form = EventForm()

    return render(request,
                  'sadmin2/generic/form.html',
                  {
                      'sadmin2_menu_main_active': 'events',
                      'sadmin2_breadcrumbs_active': 'events_create',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_events,
                      'sadmin2_menu_tab_active': 'events_create',

                      'form': form
                  })

@sadmin_prerequisites
def register_payments(request):

    payments = []

    if request.method == 'POST':
        form = RegisterPaymentForm(request.POST)

        if form.is_valid():

            result = form.cleaned_data

            payment = Payment.objects.create(attendee=result['attendee'],
                                             amount=result['payment'],
                                             signee=request.user)

            payment_registered_source.trigger(result['attendee'].user,
                                              attendee=result['attendee'],
                                              payment=payment)

            attendee = result['attendee']

            messages.success(request, _('Payment for %s has been registered successfully') % attendee.user.username)

            if not attendee.in_balance():
                # TODO Add a link to the attendee overview
                messages.warning(request, _('Payment did match the payment due. Please review the status of this person <a href="%s">here</a>') % '#')

            return HttpResponseRedirect(reverse('events_register_payments'))

    else:
        form = RegisterPaymentForm()

    return render(request,
                  'sadmin2/generic/form.html',
                  {
                      'sadmin2_menu_main_active': 'events',
                      'sadmin2_breadcrumbs_active': 'events_register_payments',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_events,
                      'sadmin2_menu_tab_active': 'events_register_payments',

                      'form': form
                  })

