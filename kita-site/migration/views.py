# coding=UTF-8

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

import core.models as coremodels

import migration.forms

def vanillaforum(request, template_name="migration/vanillaforum.html", form_class=migration.forms.VanillaForumForm):
        if request.method == 'POST':
                form = form_class(request.POST)
                if form.is_valid():
                        request.session["migration.userAuthenticated"] = True
                        request.session["migration.userUsername"] = form.cleaned_data["username"]
                        return HttpResponseRedirect(reverse("migrate_vanillaforum_step2"))
        else:
                form = form_class()
                
        return render_to_response(template_name, 
                                  { "form" : form }, 
                                  context_instance=RequestContext(request))

def vanillaforumStep2(request, template_name="migration/vanillaforumStep2.html", form_class=migration.forms.MigrationForm):

        # if the migration.userAuthenticated session variable is unset/false, then redirect the user to the migration login page
        if not request.session.get("migration.userAuthenticated", False):
                return HttpResponseRedirect(reverse("migrate_vanillaforum"))
        
        # Check if the forum user still hasent been migrated, if it has been migrated redirect to the done page.
        if userHasMigrated(request.session["migration.userUsername"]):
                return HttpResponseRedirect(reverse("migrate_vanillaforum_done"))
        
        if request.method == 'POST':
                # Inject the username into the form, forcing the user to register with this username.
                post = request.POST.copy()
                post.appendlist("username", request.session["migration.userUsername"])
                
                form = form_class(post, user=request.session["migration.userUsername"])
                if form.is_valid():
                        # Save the forum user and create a new selvbetjening user
                        form.save()
                        
                        # unset the sessions vars, so the user cant reedit this form
                        request.session["migration.userAuthenticated"] = False
                        request.session["migration.userUsername"] = ""
                        
                        return HttpResponseRedirect(reverse("migrate_vanillaforum_done"))
        else:
                vf = coremodels.VanillaForum()
                forumUser = vf.fetchUser(request.session["migration.userUsername"])
                form = form_class(user=request.session["migration.userUsername"],
                                  initial={"username" : request.session["migration.userUsername"], 
                                           "first_name" : forumUser[1], 
                                           "last_name" : forumUser[2],
                                           "email" : forumUser[3], })
                
        return render_to_response(template_name, 
                                  { "form" : form }, 
                                  context_instance=RequestContext(request))        

def userHasMigrated(username):
        try:
                user = User.objects.get(username__exact=username)
        except User.DoesNotExist:
                return False
        
        return True
