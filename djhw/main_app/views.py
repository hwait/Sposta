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
from django.utils import translation
from django.conf import settings

class UserProfile(View):
    def get(self, request):
        params=dict()
        user = User.objects.get(pk=request.user.id)
        if not Profile.objects.filter(user=user).exists():
            language=settings.LANGUAGE_CODE
        else:
            language=user.profile.lang
        request.session[translation.LANGUAGE_SESSION_KEY] = language
        translation.activate(language)
        params['timezones']=pytz.common_timezones
        params['langcode']=language
        params['languages']=settings.LANGUAGES
        return render(request,'app/userprofile.html',params)

    def post(self, request):
        params=dict()
        request.session['django_timezone'] = request.POST['timezone']
        language = request.POST.get('lang', settings.LANGUAGE_CODE)
        translation.activate(language)
        request.session[translation.LANGUAGE_SESSION_KEY] = language
        user = User.objects.get(pk=request.user.id)
        if not Profile.objects.filter(user=user).exists():
            Profile.objects.create(user=user)
        user.profile.timezone = request.POST['timezone']
        user.profile.lang = language
        if request.POST['fname']!=user.first_name:
            user.first_name=request.POST['fname']
        if request.POST['lname']!=user.last_name:
            user.last_name=request.POST['lname']
        user.save()
        return redirect('/')    

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    if request.user.id==None:
        language=settings.LANGUAGE_CODE
    else:
        user = User.objects.get(pk=request.user.id)
        if not Profile.objects.filter(user=user).exists():
            language=settings.LANGUAGE_CODE
        else:
            language=user.profile.lang
    request.session[translation.LANGUAGE_SESSION_KEY] = language
    translation.activate(language)
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

