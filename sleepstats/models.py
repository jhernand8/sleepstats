from django.db import models

# Object for a particular meal - where, when, meal, what had, who else was there, etc.
class Meal(models.Model):
  date = models.DateField()
  meal = models.TextField()
  venue = models.TextField()
  yelpUrl = models.TextField()
  food = models.TextField()
  attendee = models.TextField()
  meal_id = models.AutoField(primary_key = True)

# Object for tracking restaurants to try
class RestaurantToTry(models.Model):
  yelpUrl = models.TextField()
  venue = models.TextField()
  notes = models.TextField()
  area = models.TextField()
  food = models.TextField()

# Object for other things tracking.
class Other(models.Model):
  date = models.DateField()
  type = models.TextField()
  desc = models.TextField()
  attendee = models.TextField()
  other_id = models.AutoField(primary_key = True)

# One night of sleep
class SleepInstance(models.Model):
  starttime = models.DateTimeField()
  endtime = models.DateTimeField()
  minutes = models.IntegerField()
  sleepQuality = models.IntegerField() 
