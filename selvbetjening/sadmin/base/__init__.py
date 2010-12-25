from django.contrib.admin.helpers import AdminForm

def admin_formize(form):
    return AdminForm(form,
                     form.fieldsets,
                     {})