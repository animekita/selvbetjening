from django.conf import settings

from selvbetjening import utility

class DefaultMembershipController(object):
    """
    Simple membership manager where all users are always members.
    
    Constratins:
    - Only one possible selected membership for each invoice.
    """
    _choices = []
    
    @staticmethod
    def is_member(user, event=None):
        return True
    
    @classmethod
    def get_membership_choices(cls, user, event=None):
        return cls._choices
    
    @staticmethod
    def select_membership(user, membership, event=None, invoice=None):
        return invoice
    
    @staticmethod
    def get_membership(user, invoice):
        return
    
    @staticmethod
    def cancel_membership(user, invoice):
        return
        
    
MembershipController = DefaultMembershipController  
    
if hasattr(settings, 'MEMBERSHIP_CONTROLLER'):
    MembershipController = utility.import_function(settings.MEMBERSHIP_CONTROLLER)
    