from django.contrib.admin.helpers import AdminForm
    
class AdminFormSet(object):
    def __init__(self, forms, formset):
        self.management_form = formset.management_form
        self.forms = forms
        
    def __iter__(self):
        return self.forms.__iter__()
    
def admin_formize(form):
    return AdminForm(form,
                     form.fieldsets,
                     {})

def admin_formize_set(formset):
    forms = [admin_formize(form) for form in formset]
    return AdminFormSet(forms, formset)