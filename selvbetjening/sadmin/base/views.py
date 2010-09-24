from django.shortcuts import render_to_response
from django.template import RequestContext

def dashboard(request,
              template_name='sadmin/base/dashboard.html'):

    return render_to_response(template_name,
                              context_instance=RequestContext(request))