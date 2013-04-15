import datetime
from google.appengine.ext import db

class sleepinstance(db.Model):
  starttime = db.DateTimeProperty(required=True)
  endtime = db.DateTimeProperty(required=True)
  minutes = db.IntegerProperty(required=True)
  sleepQuality = db.IntegerProperty(required=True) 
