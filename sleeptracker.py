import webapp2
from google.appengine.api import users
import jinja2
import os
import email, getpass, imaplib, os
from time import mktime
from datetime import datetime
from datetime import timedelta
from datetime import date
import time
from string import Template
from sleepinstance import sleepinstance
from collections import namedtuple
import logging

jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

DataForDate = namedtuple('DataForDate', ['date', 'minutes', 'avgToDate', 'sleepDebtToDate'], verbose=True);

class GroupByType:
  DAY = 1
  WEEK = 2
  MONTH = 3
class MainPage(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user();

    groupTypeStr = self.request.get("groupType")
    groupType = GroupByType.DAY;
    groupInt = 1;
    if (not groupTypeStr is None) and not groupTypeStr == '':
      groupInt = int(groupTypeStr)
    if groupInt == GroupByType.WEEK:
      groupType = GroupByType.WEEK
    if groupInt == GroupByType.MONTH:
      groupType = GroupByType.MONTH 
    dataByDate = self.getDataByDate(groupType);
    latestData = None
    mostRecentDate = None;
    for dataDate in dataByDate:
      if latestData is None:
        mostRecentDate = dataDate
        latestData = dataByDate[dataDate]
      elif dataDate > mostRecentDate:
        mostRecentDate = dataDate
        latestData = dataByDate[dataDate]
    template = jinja_environment.get_template('sleepDataTemplate.html');
    templateValues = {
      'test': "test aldsjasldj",
      'dateData': dataByDate,
      'currentAvg': latestData.avgToDate,
      'currentDebt': latestData.sleepDebtToDate,
      'fullByDay': (60*8),
      'fullByWeek': (60*8*7),
      'fullByMonth': (60*8*30.5),
      'sevenByDay': (60*7),
      'sevenByWeek': (60*7*7),
      'sevenByMonth': (60*7*30.5),
      'dateKeys': sorted(dataByDate.keys())}
    self.response.out.write(template.render(templateValues))

  def getDataByDate(self, groupByType):
    query = sleepinstance.all();
    query.order("starttime");
    dateToData = {};
    sleepToDate = 0;
    numNights = 0;
    nightDates = [];
    for result in query.run():
      resdate = self.getDateForStart(result.starttime);
      nightDate = date(day=resdate.day, month=resdate.month, year=resdate.year);
      if groupByType == GroupByType.WEEK:
        resdate = self.getWeekStart(resdate)
      if groupByType == GroupByType.MONTH:
        resdate = self.getMonthStart(resdate)
      sleepToDate = sleepToDate + result.minutes;
      mins = result.minutes;
      if resdate in dateToData:
        mins = mins + dateToData[resdate].minutes;
      if not nightDate in nightDates:
        numNights = numNights + 1;
      nightDates.append(nightDate);
      debt = numNights * 8 *60 - sleepToDate;

      logging.info("   " + str(nightDate) + ": " + str(debt) + ": " + str(sleepToDate) + ": " + str(numNights) + ": " + str(mins))
      avgsl = sleepToDate / numNights
      if groupByType == GroupByType.WEEK:
        avgsl= avgsl * 7;
      elif groupByType == GroupByType.MONTH:
        avgsl = avgsl * 30.5
      nightData = DataForDate(date = resdate,
                              minutes = mins,
                              avgToDate = int(avgsl),
                              sleepDebtToDate = debt);
      dateToData[resdate] = nightData;
    return dateToData;
  def getDateForStart(self, startT):
    hour = startT.hour;
    sDate = startT.date();
    if hour < 10:
      sDate = sDate - timedelta(days = 1);
    return sDate;

  def getWeekStart(self, origDate):
    origWeekday = origDate.weekday()
    weekStart = origDate - timedelta(days = origWeekday)
    return weekStart

  def getMonthStart(self, origDate):
    return origDate.replace(day=1);
app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)
