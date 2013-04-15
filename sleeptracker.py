import webapp2
from google.appengine.api import users
import jinja2
import os
import email, getpass, imaplib, os
from time import mktime
from datetime import datetime
from datetime import timedelta
import time
from string import Template
from sleepinstance import sleepinstance
from collections import namedtuple

jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

DataForDate = namedtuple('DataForDate', ['date', 'minutes', 'avgToDate', 'sleepDebtToDate'], verbose=True);

class MainPage(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user();

    dataByDate = self.getDataByDate();
    template = jinja_environment.get_template('sleepDataTemplate.html');
    templateValues = {
      'test': "test aldsjasldj",
      'dateData': dataByDate,
      'dateKeys': sorted(dataByDate.keys())}
    self.response.out.write(template.render(templateValues))

  def getDataByDate(self):
    query = sleepinstance.all();
    query.order("starttime");
    dateToData = {};
    sleepToDate = 0;
    numNights = 0;
    for result in query.run():
      resdate = self.getDateForStart(result.starttime);
      sleepToDate = sleepToDate + result.minutes;
      mins = result.minutes;
      if resdate in dateToData:
        mins = mins + dateToData[resdate].minutes;
      else:
        numNights = numNights + 1;
      debt = numNights * 8 *60 - sleepToDate;
      nightData = DataForDate(date = resdate,
                              minutes = mins,
                              avgToDate = int(sleepToDate / numNights),
                              sleepDebtToDate = debt);
      dateToData[resdate] = nightData;
    return dateToData;
  def getDateForStart(self, startT):
    hour = startT.hour;
    sDate = startT.date();
    if hour < 10:
      sDate = sDate - timedelta(days = 1);
    return sDate;
app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)
