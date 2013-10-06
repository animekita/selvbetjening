from urllib2 import urlopen
from xml.etree import ElementTree

from django.core.management.base import NoArgsCommand
from django.utils.http import urlquote

from selvbetjening.core.members.models import User, UserLocation, UserProfile
from selvbetjening.core.members.shortcuts import get_or_create_profile

API_URL = 'http://maps.googleapis.com/maps/api/geocode/xml?address=%s&sensor=false'


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        users = UserProfile.objects.filter(location=None)

        for user in users:
            UserLocation.objects.create(user=user, expired=True)
            
        locations = UserLocation.objects.filter(expired=True)[:50]
        
        for location in locations:
            location.expired = False

            profile, created = UserProfile.objects.get(pk=location.user.pk)

            if profile.street == '' or \
               (profile.postalcode is None or profile.city == ''):
                # no address, ignore
                location.save()
                continue
            
            address = '%s %s %s %s' % (profile.street,
                                       profile.postalcode,
                                       profile.city,
                                       profile.country)
            
            url = API_URL % urlquote(address)
            
            response = urlopen(url)
            response_content = response.read()
            response.close()
            
            xml = ElementTree.fromstring(response_content)
            
            try:                
                result = xml.find("result")
                geometry = result.find("geometry")
                loc = geometry.find("location")
                lat = float(loc.find("lat").text)
                lng = float(loc.find("lng").text)
                
            except (AttributeError, ValueError):
                # no match, ignore
                location.save()
                continue
            
            location.lat = lat
            location.lng = lng
            location.save()