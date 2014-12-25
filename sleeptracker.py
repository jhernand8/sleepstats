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
AvgsForPrevDays = [1, 7, 14, 21, 30, 60, 90, 180, 365, 730];
class GroupByType:
  DAY = 1
  WEEK = 2
  MONTH = 3
class MainPage(webapp2.RequestHandler):
  def parseGroupType(self):
    groupTypeStr = self.request.get("groupType")
    groupType = GroupByType.DAY;
    groupInt = 1;
    if (not groupTypeStr is None) and not groupTypeStr == '':
      groupInt = int(groupTypeStr)
    if groupInt == GroupByType.WEEK:
      groupType = GroupByType.WEEK
    if groupInt == GroupByType.MONTH:
      groupType = GroupByType.MONTH 
    return groupType;

  def get(self):
    user = users.get_current_user();
    groupType = self.parseGroupType();
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
    avgOverPeriods = self.computeSummData()
    template = jinja_environment.get_template('sleepDataTemplate.html');
    templateValues = {
      'test': "test aldsjasldj",
      'dateData': dataByDate,
      'currentDebt': latestData.sleepDebtToDate,
      'fullByDay': (60*8),
      'fullByWeek': (60*8*7),
      'sevenByDay': (60*7),
      'sevenByWeek': (60*7*7),
      'summData': avgOverPeriods,
      'summKeys': sorted(avgOverPeriods.keys()),
      'dateKeys': sorted(dataByDate.keys())}
    self.response.out.write(template.render(templateValues))

  # Computes some summary data such as average sleep over different periods
  # putting them into a map and returning the map.
  def computeSummData(self):
    avgData = {}
    dataByDate = self.getDataByDate(GroupByType.DAY);
    sortedDates = sorted(dataByDate.keys(), reverse=True)
    dayCount = 0;
    summSleep = 0
    numDays = len(sortedDates)
    for currDay in sortedDates:
      dayCount += 1
      dataForDay = dataByDate[currDay]
      summSleep += dataForDay.minutes
      if dayCount in AvgsForPrevDays or dayCount == numDays:
        avgData[dayCount] = int(summSleep / dayCount)
    
    nowDate = date.today();
    avgData["prevYear"] = self.avgOverPeriod(dataByDate, lambda x: x.year == (nowDate.year - 1))
    avgData["currYear"] = self.avgOverPeriod(dataByDate, lambda x: x.year == nowDate.year)
    # mostly works but not always, timedelta does not have a months feature
    prevMonth = nowDate - timedelta(days = 30)
    avgData["prevMonth"] = self.avgOverPeriod(dataByDate, lambda x: x.year == prevMonth.year and x.month == prevMonth.month)
    avgData["currMonth"] = self.avgOverPeriod(dataByDate, lambda x: x.year == nowDate.year and x.month == nowDate.month)
    prevSun = date.today()
    for i in range(1, 8):
      day = date.today - timedelta(days = i)
      if day.weekday() == 6:
        prevSun = day
        break
    avgData["currWeek"] = self.avgOverPeriod(dataByDate, lambda x: x >= prevSun)
    
    avgData["prevWeek"] = self.avgOverPeriod(dataByDate,
        lamdba x: x < prevSun and (prevSun - timedelta(days = 7)) >= x)
    return avgData;

  # PeriodFN takes a date and returns true if the data for that date should be included
  # to compute the average.
  def avgOverPeriod(self, dataByDate, periodFn):
    dayCount = 0
    summSleep = 0
    for day in dataByDate.keys():
      if periodFn(day):
        dayCount += 1
        summSleep += dataByDate[day].minutes
    if summSleep == 0:
      return 0
    return summSleep / dayCount

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
