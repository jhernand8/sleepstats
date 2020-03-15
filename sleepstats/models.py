from django.db import models

class SleepInstance(models.Model):
  starttime = db.DateTimeProperty(required=True)
  endtime = db.DateTimeProperty(required=True)
  minutes = db.IntegerProperty(required=True)
  sleepQuality = db.IntegerProperty(required=True) 
