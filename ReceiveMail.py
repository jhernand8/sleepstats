import logging
import webapp2
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from sleepinstance import sleepinstance
from time import mktime
from datetime import datetime
from datetime import timedelta
import time
class ReceiveMail(InboundMailHandler):
  def receive(self, msg):
    contents = "";
    msgbody = msg.bodies('text/plain');
    if hasattr(msg, 'attachments'):
      contents = msg.attachments[0][1].decode();
    else:
      for header, body in msgbody:
        contents = body.decode();
    lines = contents.split("\n");
    # find most recent entry in db so we can ignore
    # all data that is older than it in the email
    query = sleepinstance.all();
    query.order("-starttime");
    newestentry = query.get();
    isFirst = True;
    for line in lines:
      if isFirst:
        isFirst = False;
        continue;
      if not line:
        continue;
      sleepObj = self.getSleepInstance(line);
      # only add newer entries
      if (not newestentry) or sleepObj.starttime > newestentry.starttime:
        sleepObj.put();

  def getSleepInstance(self, line):
    data = line.split(";");
    timeFormat = "%Y-%m-%d %H:%M:%S";
    startt = time.strptime(data[0], timeFormat);
    endt = time.strptime(data[1], timeFormat);

    startdt = datetime.fromtimestamp(mktime(startt));
    enddt = datetime.fromtimestamp(mktime(endt));

    duration = enddt - startdt;
    mins = int(duration.seconds / 60);

    squality = data[2][:-1];
    sleepinst = sleepinstance(starttime=startdt,
                              endtime = enddt,
                              minutes = mins,
                              sleepQuality = int(squality));
    return sleepinst;
app = webapp2.WSGIApplication([ReceiveMail.mapping()], debug=True)
