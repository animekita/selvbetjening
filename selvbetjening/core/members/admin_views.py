# -- encoding: utf-8 --
from datetime import date

from django.utils.translation import gettext as _
from django.contrib.admin.helpers import AdminForm
from django.shortcuts import render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.db.models import Min, Max
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User

from selvbetjening.core.members.models import UserProfile, to_age

from forms import AdminSelectMigrationUsers
from processor_handlers import user_migration_processors

def user_migration(request,
                   model_admin,
                   admin_site,
                   template_name='admin/auth/user/migration.html',
                   confirm_template_name='admin/auth/user/migration_confirm.html'):

    if not model_admin.has_change_permission(request, None):
        raise PermissionDenied

    view_processors = ''

    if request.method == 'POST':
        form = AdminSelectMigrationUsers(request.POST)

        if form.is_valid():
            # calculate changes
            old_user = User.objects.get(pk=form.cleaned_data['old_user'])
            new_user = User.objects.get(pk=form.cleaned_data['new_user'])

            handler = user_migration_processors.get_handler(request, old_user, new_user)

            if request.POST.has_key('do_migration') and handler.is_valid():
                handler.migrate()
                request.user.message_set.create(message=_('User account migration accomplished.'))
                return HttpResponseRedirect(reverse('admin:auth_user_migration'))
            else:
                view_processors = handler.render_function()
                pass

    else:
        form = AdminSelectMigrationUsers()

    adminform = AdminForm(form,
                          [(None, {'fields': form.base_fields.keys()})],
                          {}
                          )

    return render_to_response(template_name,
                              {'adminform' : adminform,
                               'view_processors' : view_processors},
                              context_instance=RequestContext(request))

def user_age_chart(min_age=5, max_age=80):
    cur_year = date.today().year

    # The graph looks stupid if we allow ages 0 and 100 et al.
    # Enforce sane limitations, lets say min 5 and max 80

    usersprofiles = UserProfile.objects.select_related()\
                                       .filter(dateofbirth__lt=date(cur_year-min_age, 1, 1))\
                                       .filter(dateofbirth__gt=date(cur_year-max_age, 1, 1))

    if usersprofiles.count() == 0:
        return None

    age_stats = usersprofiles.aggregate(min=Max('dateofbirth'),
                                        max=Min('dateofbirth'))

    age_stats['max'], age_stats['min'] = (to_age(age_stats['max']),
                                          to_age(age_stats['min']))

    age_span = [0] * (age_stats['max'] - age_stats['min'] + 1)

    sum = count = 0
    for usersprofile in usersprofiles:
        age = usersprofile.get_age()

        age_span[age - age_stats['min']] += 1
        sum += age
        count += 1

    return {'age_labels': range(age_stats['min'], age_stats['max'] + 1),
            'age_data': age_span,
            'min': age_stats['min'],
            'max': age_stats['max'],
            'avg': float(sum)/float(count),
            'max_limit': max_age,
            'min_limit': min_age}

def user_join_chart():
    users = User.objects.all()

    if users.count() == 0:
        return None

    join_stats = users.aggregate(max=Max('date_joined'),
                                 min=Min('date_joined'))

    def diff_in_months(ref_date, date):
        return (date.year - ref_date.year) * 12 + (date.month - ref_date.month)

    max_in_months = diff_in_months(join_stats['min'], join_stats['max'])

    join_span = [0] * (max_in_months + 1)

    for user in users:
        join_month = diff_in_months(join_stats['min'], user.date_joined)

        join_span[join_month] += 1

    join_span_acc = []
    acc = 0
    for item in join_span:
        acc = acc + item
        join_span_acc.append(acc)

    labels = []
    for x in range(0, max_in_months + 1):
        new_month = (join_stats['min'].month + x) % 12

        if new_month == 0:
            new_month = 1

        month = date(year=join_stats['min'].year + (join_stats['min'].month + x) / 12,
                     month=new_month,
                     day=1)

        labels.append(month.strftime("%B %Y"))

    return {'join_labels': labels,
            'join_data1': join_span,
            'join_data2': join_span_acc}

def user_statistics(request,
                    model_admin,
                    template_name='admin/auth/user/statistics.html',
                    template_nodata_name='admin/auth/user/no_statistics.html'):

    if not model_admin.has_change_permission(request, None):
        raise PermissionDenied

    join_data = user_join_chart()
    age_data = user_age_chart()

    if join_data is None and age_data is None:
        return render_to_response(template_nodata_name, context_instance=RequestContext(request))

    if join_data is None:
        join_data = {}

    if age_data is None:
        age_data = {}

    age_data.update(join_data)

    return render_to_response(template_name,
                              age_data,
                              context_instance=RequestContext(request))
