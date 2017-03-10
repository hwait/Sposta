import pytz

from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from main_app.models import Profile

class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tzname = request.session.get('django_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        elif request.user.id==None:
            timezone.activate('UTC')
        else:
            try:
                profile = Profile.objects.get(user=request.user)
                if profile.timezone:
                    request.session['django_timezone'] = profile.timezone
                    timezone.activate(pytz.timezone(profile.timezone))
            except Profile.DoesNotExist:
                timezone.activate('UTC')
            