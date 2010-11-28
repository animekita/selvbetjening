from models import Entry

def log(module, category, message, request=None, event=None):
    entry = {'module' : module,
             'category' : category,
             'message' : message}

    if request is not None:
        entry['ip'] = request.META.get('REMOTE_ADDR', '?.?.?.?')

        if not request.user.is_anonymous():
            entry['user'] = request.user

    if event is not None:
        entry['event'] = event

    Entry.objects.create(**entry)