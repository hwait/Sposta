"""
Definition of urls for sposta.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views

import main_app.forms
import main_app.views
import betfair_app.views
import sposta_app.views
import livescores.views
import oddsportal.views

# Uncomment the next lines to enable the admin:
# from django.conf.urls import include
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    # Examples:
    url(r'^$', main_app.views.home, name='home'),
    url(r'^contact$', main_app.views.contact, name='contact'),
    url(r'^about', main_app.views.about, name='about'),
    url(r'^login/$',
        django.contrib.auth.views.login,
        {
            'template_name': 'app/login.html',
            'authentication_form': main_app.forms.BootstrapAuthenticationForm,
            'extra_context':
            {
                'title': 'Log in',
                'year': datetime.now().year,
            }
        },
        name='login'),
    url(r'^logout$',
        django.contrib.auth.views.logout,
        {
            'next_page': '/',
        },
        name='logout'),
    url(r'^op', oddsportal.views.Oddsportal.as_view()),
    url(r'^api/op', oddsportal.views.OddsportalApi.as_view()),
    url(r'^sposta/stat', sposta_app.views.Stats.as_view(), name='stats'),
    url(r'^livescores/inspect', livescores.views.Inspect.as_view(), name='lsinspect'),
    url(r'^bf/inspect', betfair_app.views.Inspect.as_view(), name='bfinspect'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
]
