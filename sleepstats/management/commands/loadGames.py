from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder
from urllib.request import urlopen
import datetime
import json
import time
from bs4 import BeautifulSoup

# Command
class Command(BaseCommand):
  def handle(self, *args, **options):
    return;
