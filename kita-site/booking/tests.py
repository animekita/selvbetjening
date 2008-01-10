from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth import models as auth_models

from booking import models, forms

class CinemaModelTestCase(TestCase):
 
    def setUp(self):
                self.cinema = models.Cinema.objects.create(name='c1', 
                                              starttime=datetime(2008, 2, 1, 13), 
                                              endtime=datetime(2008, 2, 3, 18), 
                                              open_for_reservations=True)
                
                self.cinema2 = models.Cinema.objects.create(name='c2', 
                                              starttime=datetime(2008, 2, 1, 13), 
                                              endtime=datetime(2008, 2, 3, 18), 
                                              open_for_reservations=True)
                
                models.Reservation.objects.create(cinema=self.cinema2,
                                                  starttime=datetime(2008, 2, 1, 14),
                                                  endtime=datetime(2008, 2, 1, 16),
                                                  movie_title='movie 1',
                                                  description='desc')
                models.Reservation.objects.create(cinema=self.cinema2,
                                                  starttime=datetime(2008, 2, 1, 19),
                                                  endtime=datetime(2008, 2, 1, 21),
                                                  movie_title='movie 2',
                                                  description='desc')
    
    def test_valid_booking_no_reservations(self):
        self.assertTrue(self.cinema.is_valid_reservation(datetime(2008, 2, 2, 13), 
                                                    datetime(2008, 2, 2, 15)))
        
    def test_invalid_booking_no_reservations(self):
        self.assertFalse(self.cinema.is_valid_reservation(datetime(2008, 2, 2, 13), 
                                                    datetime(2008, 4, 2, 15)))
        
    def test_valid_booking(self):
        self.assertTrue(self.cinema2.is_valid_reservation(datetime(2008, 2, 1, 16), 
                                                    datetime(2008, 2, 1, 19)))
    def test_valid_booking_later(self):
        self.assertTrue(self.cinema2.is_valid_reservation(datetime(2008, 2, 2, 16), 
                                                    datetime(2008, 2, 2, 19)))

    def test_invalid_booking(self):
        self.assertFalse(self.cinema2.is_valid_reservation(datetime(2008, 2, 1, 15), 
                                                    datetime(2008, 2, 1, 17)))
        
    def test_invalid_booking_inside(self):
        self.assertFalse(self.cinema2.is_valid_reservation(datetime(2008, 2, 1, 14), 
                                                    datetime(2008, 2, 1, 16)))

    def test_invalid_booking_inside_partial(self):
        self.assertFalse(self.cinema2.is_valid_reservation(datetime(2008, 2, 1, 15), 
                                                    datetime(2008, 2, 1, 16)))
        