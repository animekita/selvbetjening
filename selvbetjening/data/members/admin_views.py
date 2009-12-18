def create_user(request,
                template_name='admin/members/create_user.html'):
    
    
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            event.add_attendee(user)

            return HttpResponseRedirect(reverse('admin:auth_user_changelist'))

    else:
        form = RegistrationForm()

    adminform = AdminForm(form,
                          [(None, {'fields': form.base_fields.keys()})],
                          {}
                          )

    return render_to_response(template_name,
                              {'adminform': adminform},
                              context_instance=RequestContext(request))