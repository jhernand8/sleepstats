from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django import http
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe
import json
import datetime
from json import JSONEncoder

def home(request):
  return HttpResponse("Success");
