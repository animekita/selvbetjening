def write(request, message):
    """
    Write a message to a user, currently only logged-in users supported.
    
    This is a quick wrapper around the build-in functionality in django. Later
    it will be extended to support anonymous users.
    
    """
    request.session['messaging_message'] = message
    
def read(request):
    message = None
    
    if request.session.get('messaging_message'):
        message = request.session['messaging_message']
        del(request.session['messaging_message'])
    
    return message