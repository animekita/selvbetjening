# -- encoding: utf-8 --

#from django import shortcuts
#from django.utils.translation import gettext as _
#from django.contrib.admin.views.decorators import staff_member_required
#from django.shortcuts import render_to_response, get_object_or_404
#from django.template import RequestContext
#from django.shortcuts import render_to_response
#from django.http import HttpResponseRedirect
#from django.core.urlresolvers import reverse

#from django.contrib.admin.views.main import ChangeList
#from django.contrib.admin.helpers import AdminForm
#from django.contrib.auth.models import User

#from selvbetjening.core.invoice.models import Invoice, Payment
#from selvbetjening.core.members.forms import RegistrationForm

#from processor_handlers import change_selection_processors, checkin_processors
#from models import Event, Attend, AttendState
#from forms import PaymentForm

#def billing(request, attend_id,
            #template_name='admin/events/attend/billing.html'):

    #attendee = shortcuts.get_object_or_404(Attend, pk=attend_id)
    #event = attendee.event

    #payment = Payment(revision=attendee.invoice.latest_revision,
                      #amount=attendee.invoice.unpaid,
                      #note=_('Paid at %(event)s') % {'event' : event.title})

    #if request.method == 'POST':
        #form = PaymentForm(request.POST, instance=payment)

        #if form.is_valid():
            #form.save()

        #return HttpResponseRedirect(reverse('admin:events_attend_billing', args=[attendee.pk]))

    #else:
        #form = PaymentForm(instance=payment)

    #adminform = AdminForm(form,
                          #[(None, {'fields': form.base_fields.keys()})],
                          #{}
                          #)

    #return render_to_response(template_name,
                          #{'event' : event,
                           #'attendee' : attendee,
                           #'adminform' : adminform,
                          #},
                          #context_instance=RequestContext(request))

#def checkout(request,
            #attend_id,
            #template_name='admin/events/attend/checkout.html'):

    #attendee = shortcuts.get_object_or_404(Attend, pk=attend_id)
    #event = attendee.event

    #if not attendee.state == AttendState.attended:
        #return HttpResponseRedirect(get_checkin_list_url(attendee))

    #if request.method == 'POST':
        #attendee.state = AttendState.accepted
        #attendee.save()

        #request.user.message_set.create(message=u'%s checked out for event %s' % (attendee.user, attendee.event))

        #return HttpResponseRedirect(get_checkin_list_url(attendee))

    #return render_to_response(template_name,
                              #{'event' : event,
                               #'attendee' : attendee},
                              #context_instance=RequestContext(request))

#def checkin(request, attend_id,
            #template_name='admin/events/attend/checkin.html'):

    #attendee = shortcuts.get_object_or_404(Attend, pk=attend_id)
    #event = attendee.event

    #if attendee.state == AttendState.attended:
        #return HttpResponseRedirect(get_checkin_list_url(attendee))

    #if request.method == 'POST':
        #if request.POST.has_key('do_checkin_and_pay') and not attendee.invoice.in_balance():
            #Payment.objects.create(revision=attendee.invoice.latest_revision,
                                   #amount=attendee.invoice.unpaid,
                                   #note=_('Payment at %(event)s checkin') % {'event' : attendee.event})

        #attendee.state = AttendState.attended
        #attendee.save()

        #request.user.message_set.create(message=u'%s checked in for event %s' % (attendee.user, attendee.event))

        #return HttpResponseRedirect(get_checkin_list_url(attendee))

    #handler = checkin_processors.get_handler(request, attendee)

    #checkin_rendered = handler.view()

    #return render_to_response(template_name,
                              #{'event' : event,
                               #'attendee' : attendee,
                               #'checkin_rendered': checkin_rendered},
                              #context_instance=RequestContext(request))
