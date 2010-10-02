from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q
import operator

from selvbetjening.sadmin.base.sadmin import SAdminContext

def _search(request):
    query = request.GET.get('search', None)
    qs = []
    
    search_fields = ['first_name', 'last_name', 'username']
    
    if query is not None:  
        qs = User.objects.all()
        
        for term in query.split():
            or_queries = [Q(**{'%s__icontains' % field_name: term}) for field_name in search_fields]
            qs = qs.filter(reduce(operator.or_, or_queries))
            
    return (query, qs)

def list(request,
         template_name='sadmin/members/list.html'):
    query, qs = _search(request)
    
    return render_to_response(template_name,
                              {'query' : query,
                               'users' : qs},
                              context_instance=SAdminContext(request))


def view(request,
         username,
         template_name='sadmin/members/view.html'):

    user = get_object_or_404(User, username=username)
    
    return render_to_response(template_name,
                              {'user' : user},
                              context_instance=SAdminContext(request))

def ajax_search(request,
                template_name='sadmin/members/ajax/search.html'):
    query, qs = _search(request)
    
    return render_to_response(template_name,
                              {'query' : query,
                               'users' : qs},
                              context_instance=SAdminContext(request))
