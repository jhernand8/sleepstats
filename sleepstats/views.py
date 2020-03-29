from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django import http
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
import json
from time import mktime
from datetime import datetime
from datetime import timedelta
from datetime import date
from collections import namedtuple
import time
from json import JSONEncoder
from sleepstats.models import SleepInstance

DataForDate = namedtuple('DataForDate', ['date', 'minutes', 'avgToDate', 'sleepDebtToDate', 'avgForGroup', 'groupAvgToDate', 'numNights'], verbose=True);
AvgsForPrevDays = [1, 7, 14, 21, 30, 60, 90, 180, 365, 730];
class GroupByType:
  DAY = 1
  WEEK = 2
  MONTH = 3
  YEAR = 4


def parseGroupType(groupTypeStr):
  groupType = GroupByType.DAY;
  groupInt = 1;
  if (not groupTypeStr is None) and not groupTypeStr == '':
    groupInt = int(groupTypeStr)
  if groupInt == GroupByType.WEEK:
    groupType = GroupByType.WEEK
  if groupInt == GroupByType.MONTH:
    groupType = GroupByType.MONTH 
  if groupInt == GroupByType.YEAR:
    groupType = GroupByType.YEAR
  return groupType;

def home(request):
  groupType = parseGroupType(request.GET.get('groupType'));
  dataByDate = getDataByDate(groupType);
  latestData = None
  mostRecentDate = None;
  for dataDate in dataByDate:
    if latestData is None:
      mostRecentDate = dataDate
      latestData = dataByDate[dataDate]
    elif dataDate > mostRecentDate:
      mostRecentDate = dataDate
      latestData = dataByDate[dataDate]
  avgOverPeriods = computeSummData()
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
      'dateKeys': sorted(dataByDate.keys()),
      'isIndivDay': (groupType == GroupByType.DAY)}
  return render(request, 'sleepDataTemplate.html', templateValues);


# Computes some summary data such as average sleep over different periods
# putting them into a map and returning the map.
def computeSummData():
  avgData = {}
  dataByDate = getDataByDate(GroupByType.DAY);
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
      if dayCount == numDays:
        avgData["AVG"] = int(summSleep/dayCount)
  
  nowDate = date.today();
  avgData["prevYear"] = avgOverPeriod(dataByDate, lambda x: x.year == (nowDate.year - 1))
  avgData["currYear"] = avgOverPeriod(dataByDate, lambda x: x.year == nowDate.year)
  # mostly works but not always, timedelta does not have a months feature
  prevMonth = nowDate - timedelta(days = 30)
  avgData["prevMonth"] = avgOverPeriod(dataByDate, lambda x: x.year == prevMonth.year and x.month == prevMonth.month)
  avgData["currMonth"] = avgOverPeriod(dataByDate, lambda x: x.year == nowDate.year and x.month == nowDate.month)
  prevSun = date.today()
  for i in range(1, 8):
    day = date.today() - timedelta(days = i)
    if day.weekday() == 6:
      prevSun = day
      break
  avgData["currWeek"] = avgOverPeriod(dataByDate, lambda x: x >= prevSun)
  
  prevPrevSun = prevSun - timedelta(days = 7);
  avgData["prevWeek"] = avgOverPeriod(dataByDate,
      lambda x: x < prevSun and prevPrevSun <= x)
  avgData["avg"] = summSleep / dayCount;
  avgData["minToNext"] = int((int(summSleep / dayCount) + 1) * dayCount - summSleep);
  return avgData;

# PeriodFN takes a date and returns true if the data for that date should be included
# to compute the average.
def avgOverPeriod( dataByDate, periodFn):
  dayCount = 0
  summSleep = 0
  for day in dataByDate.keys():
    if periodFn(day):
      dayCount += 1
      summSleep += dataByDate[day].minutes
  if summSleep == 0:
    return 0
  return summSleep / dayCount

def getDataByDate( groupByType):
  allSleep = SleepInstance.objects.order_by("starttime").all();
  dateToData = {};
  sleepToDate = 0;
  numNights = 0;
  nightDates = [];
  for result in allSleep:
    resdate = getDateForStart(result.starttime);
    nightDate = date(day=resdate.day, month=resdate.month, year=resdate.year);
    if groupByType == GroupByType.WEEK:
      resdate = getWeekMid(resdate)
    if groupByType == GroupByType.MONTH:
      resdate = getMonthMid(resdate)
    if groupByType == GroupByType.YEAR:
      resdate = getYearMid(resdate)
    sleepToDate = sleepToDate + result.minutes;
    mins = result.minutes;
    nightsInGroup = 0;
    if resdate in dateToData:
      mins = mins + dateToData[resdate].minutes;
      nightsInGroup = dateToData[resdate].numNights;
    if not nightDate in nightDates:
      numNights = numNights + 1;
      nightsInGroup += 1
    nightDates.append(nightDate);
    debt = numNights * 8 *60 - sleepToDate;

    avgsl = sleepToDate / numNights
    avgGroup = avgsl
    if groupByType == GroupByType.WEEK:
      avgsl= avgsl * 7;
    elif groupByType == GroupByType.MONTH:
      avgsl = avgsl * 30.5
    elif groupByType == GroupByType.YEAR:
      avgsl = avgsl * 365
    nightData = DataForDate(date = resdate,
                            minutes = mins,
                            avgForGroup = int(mins / nightsInGroup),
                            avgToDate = int(avgsl),
                            groupAvgToDate = int(avgGroup),
                            numNights = nightsInGroup,
                            sleepDebtToDate = debt);
    dateToData[resdate] = nightData;
  return dateToData;
def getDateForStart(startT):
  hour = startT.hour;
  sDate = startT.date();
  if hour < 10:
    sDate = sDate - timedelta(days = 1);
  return sDate;

def getWeekMid(origDate):
  origWeekday = origDate.weekday()
  weekStart = origDate - timedelta(days = origWeekday) + timedelta(3)
  return weekStart

def getMonthMid(origDate):
  return origDate.replace(day=15);
def getYearMid(origDate):
  return origDate.replace(day=2).replace(month=7);


# Handler for receiving email with csv attachment.
@csrf_exempt
def handleMail(request):
  outStr = ""
  for k in request.POST:
    print("req: " + str(k) + "\n");
    outStr += "req: " + str(k);
  return http.HttpResponse(outStr)

def parseIntoSleepInstance(line):
  data = line.split(";");
  timeFormat = "%Y-%m-%d %H:%M:%S";
  startt = time.strptime(data[0], timeFormat);
  endt = time.strptime(data[1], timeFormat);

  startdt = datetime.fromtimestamp(mktime(startt));
  enddt = datetime.fromtimestamp(mktime(endt));

  duration = enddt - startdt;
  mins = int(duration.seconds / 60);

  squality = data[2][:-1];
  sleepinst = SleepInstance(starttime=startdt,
                            endtime = enddt,
                            minutes = mins,
                            sleepQuality = int(squality));
  return sleepinst;
