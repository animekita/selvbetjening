from django.contrib import admin

from models import Cinema, Reservation

class CinemaAdmin(admin.ModelAdmin):
    list_display = ('name', 'open_for_reservations', 'starttime', 'endtime')

admin.site.register(Cinema, CinemaAdmin)

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('cinema', 'owner', 'starttime', 'endtime', 'movie_title', 'description')

admin.site.register(Reservation, ReservationAdmin)