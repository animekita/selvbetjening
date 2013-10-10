from sadmin2 import menu
from sadmin2.decorators import sadmin_prerequisites

from mailqueue.models import MailerMessage
from sadmin2.views.generic import search_view


@sadmin_prerequisites
def queue(request):

    queryset = MailerMessage.objects.all().\
        order_by('sent', 'last_attempt', '-pk')

    columns = ('subject', 'app', 'to_address')

    context = {
        'sadmin2_menu_main_active': 'emails',
        'sadmin2_breadcrumbs_active': 'emails_queue',
        'sadmin2_menu_tab': menu.sadmin2_menu_tab_emails,
        'sadmin2_menu_tab_active': 'queue',
    }

    return search_view(request,
                       queryset,
                       'sadmin2/emails/queue_list.html',
                       'sadmin2/emails/queue_list_inner.html',
                       search_columns=columns,
                       context=context)