
from selvbetjening.core.members.models import SUser
from selvbetjening.core.events.models import Attend
from selvbetjening.sadmin2.decorators import sadmin_prerequisites
from selvbetjening.sadmin2.views.generic import search_view


@sadmin_prerequisites
def users(request):

    queryset = SUser.objects.all()
    columns = ('username', 'first_name', 'last_name', 'email')

    return search_view(request,
                       queryset,
                       'sadmin2/autocomplete/users.html',
                       'sadmin2/autocomplete/users.html',
                       search_columns=columns)


@sadmin_prerequisites
def attendees(request):

    queryset = Attend.objects.all().select_related('event', 'user')
    columns = ('event__title', 'user__username', 'user__first_name', 'user__last_name', 'user__email')

    return search_view(request,
                       queryset,
                       'sadmin2/autocomplete/attendees.html',
                       'sadmin2/autocomplete/attendees.html',
                       search_columns=columns)

