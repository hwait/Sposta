"""
Definition of urls for sposta.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views
import allauth
import main_app.forms
import main_app.views
import betfair_app.views
import sposta_app.views
import livescores.views
import oddsportal.views
from betfair_app.views import BFInspect, BFApiGet, BFApiIds,BFApiInfo
from oddsportal.views import OPInspect, OPApiGet, OPApiIds
from livescores.views import LSInspect, LSApiGet, LSApiIds
from sposta_app.views import Stats,MainInspect, ApiBind,ApiBindEvents
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^$', main_app.views.home, name='home'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^contact$', main_app.views.contact, name='contact'),
    url(r'^about', main_app.views.about, name='about'),
    #url(r'^login/$',
    #    django.contrib.auth.views.login,
    #    {
    #        'template_name': 'app/login.html',
    #        'authentication_form': main_app.forms.BootstrapAuthenticationForm,
    #        'extra_context':
    #        {
    #            'title': 'Log in',
    #            'year': datetime.now().year,
    #        }
    #    },
    #    name='login'),
    url(r'^logout$',
        django.contrib.auth.views.logout,
        {
            'next_page': '/',
        },
        name='logout'),
    url(r'^api/bf/get', BFApiGet.as_view()),
    url(r'^api/bf/ids', csrf_exempt(BFApiIds.as_view())),
    url(r'^api/bf/info', BFApiInfo.as_view()),
    url(r'^api/bindevents', csrf_exempt(ApiBindEvents.as_view())),
    url(r'^api/bind', csrf_exempt(ApiBind.as_view())),
    url(r'^api/ls/get', LSApiGet.as_view()),
    url(r'^api/ls/ids', csrf_exempt(LSApiIds.as_view())),
    url(r'^api/op/get', OPApiGet.as_view()),
    url(r'^api/op/ids', csrf_exempt(OPApiIds.as_view())),
    url(r'^sposta/stat', Stats.as_view(), name='stats'),
    url(r'^livescores/inspect', LSInspect.as_view(), name='lsinspect'),
    url(r'^odds/inspect', OPInspect.as_view(), name='opinspect'),
    url(r'^bf/inspect', BFInspect.as_view(), name='bfinspect'),
    url(r'^lines', MainInspect.as_view(), name='maininspect'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^rosetta/', include('rosetta.urls')),
]
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__/', include(debug_toolbar.urls)),
    ]
