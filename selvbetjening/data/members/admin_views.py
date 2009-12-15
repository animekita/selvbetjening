def create_user(request,
                template_name='eventmode/create_user.html'):

    event = request.eventmode.model.event

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            event.add_attendee(user)

            return HttpResponseRedirect(reverse('eventmode_change_selections',
                                                kwargs={'user_id' : user.id}))

    else:
        form = RegistrationForm()

    adminform = AdminForm(form,
                          [(None, {'fields': form.base_fields.keys()})],
                          {}
                          )

    return render_to_response(template_name,
                              {'adminform': adminform},
                              context_instance=RequestContext(request))