
from django.shortcuts import render

from selvbetjening.sadmin2.decorators import sadmin_prerequisites


@sadmin_prerequisites
def dashboard(request):

    return render(request,
                  'sadmin2/dashboard.html',
                  {
                      'sadmin2_breadcrumbs_active': 'dashboard'
                  })
