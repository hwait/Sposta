"""
Definition of views.
"""
from django.contrib.auth.models import User
from main_app.models import Profile
from django.shortcuts import render,redirect
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from django.views import View
import pytz

class UserProfile(View):
    def get(self, request):
        params=dict()
        params['timezones']=pytz.common_timezones
        return render(request,'app/userprofile.html',params)

    def post(self, request):
        params=dict()
        request.session['django_timezone'] = request.POST['timezone']
        user = User.objects.get(pk=request.user.id)
        if not Profile.objects.filter(user=user).exists():
            Profile.objects.create(user=user)
        user.profile.timezone = request.POST['timezone']
        #try:
        #    user.profile.timezone = request.POST['timezone']
        #except ObjectDoesNotExist:
        #    user.profile=Profile(timezone=request.POST['timezone'])
        user.save()
        return redirect('/')    

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )

