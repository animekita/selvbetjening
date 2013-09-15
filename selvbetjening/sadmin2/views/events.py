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
from django.utils.safestring import mark_safe

from selvbetjening.core.events.models import Event

from selvbetjening.sadmin2.forms import EventForm
from selvbetjening.sadmin2.decorators import sadmin_prerequisites
from selvbetjening.sadmin2 import menu

from generic import apply_search_query, get_search_url

@sadmin_prerequisites
def event_list(request, ajax=False):

    columns = ('title',)

    queryset = Event.objects.all()
    queryset = apply_search_query(queryset, request.GET.get('q', ''), columns)

    search_url = get_search_url(request, reverse('sadmin2:events_list_ajax'))

    return render(request,
                  'sadmin2/events/list.html' if not ajax else 'sadmin2/events/list_inner.html',
                  {
                      'sadmin2_menu_main_active': 'events',
                      'sadmin2_breadcrumbs_active': 'events',
                      'sadmin2_menu_tab': menu.sadmin2_menu_tab_events,
                      'sadmin2_menu_tab_active': 'events',

                      'search_url': mark_safe(search_url),

                      'events': queryset
                  })

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

