from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.template import Context
from models import OPMeet
from django.core import serializers
from json import dumps
from django.http import JsonResponse
import datetime

class Oddsportal(View):
    def get(self, request):
        params=dict()
        opmeets=OPMeet.objects.all()
        params['opmeets']=opmeets
        #dtadd=OPMeet.objects.latest('dtadd').dtadd
        #params['dtdiff']=(datetime.datetime.now(dtadd.tzinfo)-dtadd).seconds
        return render(request,'oddsportal.html',params)

class OddsportalApi(View):
    def get(self, request):
        params=dict()
        opmeets=OPMeet.objects.all()
        response_data = {}
        response_data['result'] = 'Success'
        response_data['message'] = serializers.serialize('json', opmeets)
        OPMeet.objects.all().delete()
        #try:
        #    response_data['result'] = 'Success'
        #    response_data['message'] = serializers.serialize('json', opmeet)
        #except:
        #    response_data['result'] = 'Error'
        #    response_data['message'] = 'Script has not ran correctly'
        return HttpResponse(JsonResponse(response_data), content_type="application/json")

    