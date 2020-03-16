from django.db import models

class SleepInstance(models.Model):
  starttime = models.DateTimeField(required=True)
  endtime = models.DateTimeField(required=True)
  minutes = models.IntegerField(required=True)
  sleepQuality = models.IntegerField(required=True) 
