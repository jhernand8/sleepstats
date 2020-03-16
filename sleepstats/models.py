from django.db import models

class SleepInstance(models.Model):
  starttime = models.DateTimeField()
  endtime = models.DateTimeField()
  minutes = models.IntegerField()
  sleepQuality = models.IntegerField() 
