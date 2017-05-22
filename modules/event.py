import math
from discord.ext.commands import Bot
from modules import util
from datetime import datetime
from tinydb import TinyDB, where
import asyncio
import pytz
import re

"""
DATABASE db-event
eventname | year | month | day | hour(24) | minute
dnd-sat   | 2017 | 4     | 11  | 13       | 30
"""
DB_NAME = "data/db-event.json"
db = None

THRESHOLD_DAY = 86400
THRESHOLD_HOUR = 3600
THRESHOLD_SOON = 300

RE_DATE = '[0-9]{1,2}[-/][0-9]{1,2}'
RE_TIME_12 = '([0-9]{1,2}(:[0-9]{2})?[ ]?[ap]m?)'
RE_TIME_24 = '[0-9]{3,4}'
RE_ZONE = '[pce][sd]t'
TIMEZONES = {
  'e': pytz.timezone('US/Eastern'),
  'c': pytz.timezone('US/Central'),
  'p': pytz.timezone('US/Pacific')
}

@asyncio.coroutine
def on_message(bot: Bot, message):
  # Ensure db is setup
  global db
  if db is None:
    db = TinyDB(DB_NAME)

  if util.sw(message, '!event set') or util.sw(message, '!event add'):
    yield from setEvent(bot, message)
    return True
  elif util.sw(message, '!event remove'):
    yield from removeEvent(bot, message)
  elif util.sw(message, '!event list'):
    yield from list(bot, message)
  elif util.isSuperUser(message.author) and util.sw(message, '!event purge'):
    yield from purge(bot, message)
  elif util.sw(message, '!event ') or message.content == '!event':
    yield from help(bot, message)

"""
Sets or updates an event. Supports lots of time and date formats.
!event set CoolEvent 4-25 4:00pm EST
!event set CoolEvent 4/25 4:00 p est
!event set CoolEvent 4-25 1600 EST
"""
@asyncio.coroutine
def setEvent(bot, message):
  # Parse the input for the event name
  try:
    if util.getArg(message.content, 2) is None:
      yield from bot.send_message(message.channel, ("ℹ Set or update an event.\n" +
                                                    "`!event set name date time timezone`"))
      return
    # Reject eventnames that are longer than 1 word
    validname = re.match('!event ((set)|(add)) [^ ]* [0-9]', message.content, re.IGNORECASE)
    if not validname:
      yield from bot.send_message(message.channel, "❌ The event's name needs to be a single word.")
      return
    eventname = util.getArg(message.content, 2)
  except Exception:
    return

  # Parse the input for the datetime
  eventtime = yield from parseEventTime(message.content)
  if eventtime is None:
    yield from bot.send_message(message.channel, ("❌ I didn't understand your date or time, try again.\n"
                                                  "`!event set name date time timezone`"))
    return

  diff = getReadableTimeDiff(eventtime - datetime.now(tz=pytz.timezone('UTC')))

  # Add the event
  if not db.search(where('eventname') == eventname):
    db.insert({
      'eventname': eventname,
      'year': eventtime.year,
      'month': eventtime.month,
      'day': eventtime.day,
      'hour': eventtime.hour,
      'minute': eventtime.minute
    })
    yield from bot.send_message(message.channel, ("✅ Event " + eventname + " added! " + diff + "\n" +
                                                  "See all events with `!event list`."))
  else:
    db.update({
      'year': eventtime.year,
      'month': eventtime.month,
      'day': eventtime.day,
      'hour': eventtime.hour,
      'minute': eventtime.minute
      },
      where('eventname') == eventname)
    yield from bot.send_message(message.channel, ("✅ Event " + eventname + " updated! " + diff + "\n" +
                                                  "See all events with `!event list`."))
  return eventtime

"""
Removes an event
!event remove CoolEvent
"""
@asyncio.coroutine
def removeEvent(bot, message):
  try:
    eventname = util.getArg(message.content, 2)
    if not db.search(where('eventname') == eventname):
      yield from bot.send_message(message.channel, "⚠ Event " + eventname + " didn't and doesn't exist.")
    else:
      db.remove((where('eventname') == eventname))
      yield from bot.send_message(message.channel, "✅ Removed the " + eventname + " event.")
  except Exception:
    return

"""
Grabs the datetime info from a user command chunk.
"""
@asyncio.coroutine
def parseEventTime(timeinput):
  timegroup = re.search(RE_DATE + ' (' + RE_TIME_12 + '|' + RE_TIME_24 + ') ' + RE_ZONE + '$', timeinput,
                        flags=re.IGNORECASE)
  if timegroup is not None:
    userdate = re.search(RE_DATE, timeinput, flags=re.IGNORECASE).group(0)
    usermonth, userday = userdate.split('-' if '-' in timeinput else '/')
    userzone = re.search(RE_ZONE, timeinput, flags=re.IGNORECASE).group(0).lower()[0]
    usertime = re.search(' ' + RE_TIME_12, timeinput, flags=re.IGNORECASE)
    if usertime is None:
      usertime = re.search(RE_TIME_24, timeinput).group(0)
      userhour = usertime[:-2]
      userminute = usertime[-2:]
    else:
      usertime = usertime.group(0)[1:]
      isAm = 'a' in usertime
      usertime = re.sub('[^0-9:]', '', usertime)
      if ':' in usertime:
        userhour, userminute = usertime.split(':')
        if not isAm and int(userhour) != 12:
          userhour = int(userhour) + 12
        elif isAm and int(userhour) == 12:
          userhour = 0
      else:
        userhour = usertime if isAm else int(usertime) + 12
        userminute = 0

    try:
      nowtime = datetime.now(tz=pytz.timezone('UTC'))
      year = nowtime.year
      eventtime = TIMEZONES[userzone].localize(
        datetime(year, int(usermonth), int(userday), int(userhour), int(userminute)))
      eventtime = eventtime.astimezone(pytz.timezone('UTC'))
      if (nowtime.month < eventtime.month or nowtime.day < eventtime.day or
              nowtime.hour < eventtime.hour or nowtime.minute < eventtime.minute):
        eventtime.replace(year=year + 1)
      return eventtime
    except Exception as e:
      print("[parseEventTime] Couldn't parse time", timeinput, e)
      return None

def getReadableTimeDiff(timediff):
  diffSeconds = timediff.total_seconds()
  if diffSeconds < 0:
    message = '(passed)'
  elif diffSeconds < THRESHOLD_SOON:
    message = '(happening in < 5 minutes!)'
  elif diffSeconds < THRESHOLD_HOUR:
    diff = int(diffSeconds // 60)
    message = '(in ' + str(diff) + util.pl(' minute', diff) + ')'
  elif diffSeconds < THRESHOLD_DAY:
    diff = int(diffSeconds // THRESHOLD_HOUR)
    message = '(in ' + str(diff) + util.pl(' hour', diff) + ')'
  else:
    diff = int(diffSeconds // THRESHOLD_DAY)
    message = '(in ' + str(diff) + util.pl(' day', diff) + ')'
  return message

"""
Purges all events.
!event purge
"""
@asyncio.coroutine
def purge(bot, message):
  db.purge()
  yield from bot.send_message(message.channel, "✅ Events cleared.")

"""
Spits out a list of all known events. Supports PST, CST, EST.
!event list (timezone)
"""
@asyncio.coroutine
def list(bot, message):
  rows = db.all()
  if not rows:
    response = 'No events saved yet.'
  else:
    userzone = util.getArg(message.content, 2)
    if userzone is None:
      userzone = pytz.timezone('US/Eastern')
    else:
      # Try to look for P, C, or E
      try:
        userzone = TIMEZONES[userzone[0]]
      except Exception:
        userzone = pytz.timezone('US/Eastern')

    nowtime = datetime.now(tz=userzone)
    response = '🗓 **Events:**'

    events = []
    # Collect the events in a pair of (time, name)
    for row in rows:
      eventtime = datetime(row['year'], row['month'], row['day'],
                           row['hour'], row['minute'], tzinfo=pytz.timezone('UTC'))
      eventtime = eventtime.astimezone(userzone)
      events.append((eventtime, row['eventname']))
    # Now print out the events in sorted order by time
    events = sorted(events)
    for eventpair in events:
      response += ('\n**' + eventpair[1] + ':** ' + eventpair[0].strftime('%b %d (%a), %I:%M%p %Z') +
                   " " + getReadableTimeDiff(eventpair[0] - nowtime))

  yield from bot.send_message(message.channel, response)

"""
Displays help.
!event
"""
@asyncio.coroutine
def help(bot, message):
  yield from bot.send_message(message.channel,
                              ("ℹ Shows a list of upcoming events!\n"
                               "`!event list`\n"
                               "`!event list PST`\n"
                               "`!event set D&D 4-11 9:00p EST`\n"
                               "`!event remove D&D`\n"
                               "(I know about EST, CST, and PST.)"))