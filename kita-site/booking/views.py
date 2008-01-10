from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required

import models, forms

def view_cinema(request, cinema_name, template_name='booking/view_cinema.html'):
    cinema = get_object_or_404(models.Cinema, name=cinema_name)
    
    return render_to_response(template_name, 
                              {'cinema' : cinema, 'reservations' : cinema.reservation_set.all().order_by('starttime')}, 
                              context_instance=RequestContext(request))

@login_required
def create_booking(request, cinema_name, template_name='booking/create_booking.html'):
    cinema = get_object_or_404(models.Cinema, name=cinema_name)
    
    if request.method == 'POST':
        form = forms.ReservationForm(request.POST, cinema=cinema)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('booking_view_cinema', kwargs={'cinema_name' : cinema.name}))
    else:
        form = forms.ReservationForm(cinema=cinema)
    
    return render_to_response(template_name,
                              {'form' : form, 'cinema' : cinema},
                              context_instance=RequestContext(request))
