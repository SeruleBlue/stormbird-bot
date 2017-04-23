from discord.ext.commands import Bot
import asyncio
import logging
import re

logging.basicConfig(level=logging.INFO)

timeZoneIter = ['P', 'C', 'E']
timeZones = {
  'E': 0,
  'C': 1,
  'P': 3
}

@asyncio.coroutine
def convertTimezone(bot: Bot, message):
  # find everything that could be a time
  timeGroups = re.finditer("\\b[0-9]{1,2}(:[0-9]{2})?[ ]?[AaPp][Mm]?[ ][EeCcPp][Ss][Tt]\\b", message.content)
  if timeGroups is None:
    return

  response = ""

  for reMatch in timeGroups:
    timeGroup = reMatch.group()
    baseZone = timeZones[timeGroup[-3].upper()]
    rawTime = timeGroup[:timeGroup.rfind(' ')]
    minute = "00"
    if ':' in rawTime:
      c = rawTime.index(':')
      hour = int(rawTime[:c])
      minute = rawTime[c+1:c+3].zfill(2)
    else:
      hour = int(re.sub("\D", "", rawTime))
    if hour > 12:
      continue
    subresponse = timeGroup + " is: "
    for zone in timeZoneIter:

      if 'a' in rawTime:
        zHour = hour + baseZone - timeZones[zone] - 12
      else:
        zHour = hour + baseZone - timeZones[zone] + (0 if hour == 12 else 12)

      ap = 'a'
      if zHour >= 12:
        zHour -= 12
        if zHour != 12:
          ap = 'p'
      if zHour == 0:
        zHour = 12
      elif zHour < 0:
        zHour += 12
        ap = 'a' if ap == 'p' else 'p'
      subresponse += str(zHour) + ":" + minute + ap + "m " + zone + "ST, "
    response += subresponse[:-2] + "\n"

  if response != "":
    return (yield from bot.send_message(message.channel, response[:-1]))