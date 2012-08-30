
from django.core.exceptions import PermissionDenied

def superuser_required(view):
    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return _inner