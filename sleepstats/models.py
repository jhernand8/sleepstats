from django.db import models

class SleepInstance(models.Model):
  starttime = models.DateTimeProperty(required=True)
  endtime = models.DateTimeProperty(required=True)
  minutes = models.IntegerProperty(required=True)
  sleepQuality = models.IntegerProperty(required=True) 
