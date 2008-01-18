from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User  

class Cinema(models.Model):
    name = models.CharField(_('cinema name'), max_length=40, unique=True)
    starttime = models.DateTimeField(_('start time'))
    endtime = models.DateTimeField(_('end time'))
    open_for_reservations = models.BooleanField(_('open for reservations'))
    
    class Admin:
        pass
    
    def is_valid_reservation(self, startdatetime, enddatetime):
        """
        First check that the reservation is inside the cinema open time slot. Then check all
        the reservations, if another reservations start or end time is inside the interval, it will
        conflict and is then invalid.
        
        """
        if startdatetime >= enddatetime:
            return False
        
        if self.starttime > startdatetime or self.endtime < enddatetime:
            return False
        
        for reservation in self.reservation_set.all():
            if reservation.starttime >= startdatetime and reservation.starttime < enddatetime:
                return False
            elif reservation.endtime > startdatetime and reservation.endtime <= enddatetime:
                return False
            
        return True

class Reservation(models.Model):
    cinema = models.ForeignKey(Cinema)
    owner = models.ForeignKey(User)
    starttime = models.DateTimeField(_('start time'))
    endtime = models.DateTimeField(_('end time'))
    movie_title = models.CharField(_('movie title'), max_length=200)
    description = models.CharField(_('description'), max_length=200, blank=True)
    
    class Admin:
        pass
    