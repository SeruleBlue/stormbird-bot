from discord.ext.commands import Bot
import asyncio
import logging
import re
import time

logging.basicConfig(level=logging.INFO)

tzToOffset = {
  "PST": -8,
  "CST": -6,
  "EST": -5
}

@asyncio.coroutine
def detectTimezones(bot: Bot, message, outputZones=None):
  # find everything that could be a time
  # 1:hour, 2:minute, 3:am/pm, 4:timezone, 5:gmt offset
  timeGroups = re.finditer("([0-9]{1,2}):([0-9]{2})?[ ]?([ap])[m]?[ ]([a-z]{3})([+-][0-9]+)?\\b", message.content, re.I)
  if timeGroups is None:
    return
  response = "⏲️ Converted time:"
  shouldReply = False
  for timeGroup in timeGroups:
    timeZone = timeGroup.expand("\\4").upper()
    gmtOff = timeGroup.expand("\\5")
    if not timeZone in tzToOffset and not gmtOff:
      continue
    hour = int(timeGroup.expand("\\1"))
    minute = int(timeGroup.expand("\\2"))
    if minute >= 60:  # screw you, buddy!
      continue
    isAm = "a" in timeGroup.expand("\\3").lower()
    if hour == 12 and isAm:
      hour = 0
    elif hour != 12 and not isAm:
      hour += 12
    fullTime = hour * 100 + minute
    response += '\n' + (yield from convertTimezone(fullTime, timeZone, gmtOff, outputZones))
    shouldReply = True
  if shouldReply:
    return (yield from bot.send_message(message.channel, response))

# !time my-time GMT+10
@asyncio.coroutine
def convertMessage(bot: Bot, message):
  outputZone = re.search("\\b\S+$", message.content, re.I)
  zone = outputZone.group(0)
  if outputZone and "GMT" in zone.upper():
    message.content = message.content[:message.content.index(zone)]
    yield from detectTimezones(bot, message, [zone])

# example args (bot, 1300, GMT, +2, [PST, -2])
@asyncio.coroutine
def convertTimezone(fullTime, inputZone, inputOffset, outputZones=None):
  if not outputZones:
    outputZones = ["PST", "CST", "EST"]
  if inputOffset == '':
    inputOffset = 0
  if inputZone in tzToOffset:
    inputOffset += tzToOffset[inputZone]

  outputs = []
  for zone in outputZones:
    # Adjust for DST
    if zone not in tzToOffset and time.localtime().tm_isdst:
      fullTime -= 100
      if fullTime < 0:
        fullTime += 2400
    if zone in tzToOffset:
      outputOffset = tzToOffset[zone]
    else:
      # Fucking ugly
      if '-' in zone:
        outputOffset = int(zone[zone.index('-')+1:])
      elif '+' in zone:
        outputOffset = int(zone[zone.index('+')+1:])
    decorators = "**" if inputOffset == outputOffset else ""
    outputs.append(decorators + timeToTime(fullTime, inputOffset, outputOffset) + ' ' + zone.upper() + decorators)
  return ', '.join(outputs)

# inputTime as a time in 24H format
# inputZone as an offset from GMT
# outputZone as an offset from GMT
# returns time in 11:20pm format
def timeToTime(inputTime, inputOffset, outputOffset):
  time = (inputTime + 100 * (int(outputOffset) - int(inputOffset))) % 2400
  ampm = "am" if time < 1200 else "pm"
  hours = time // 100
  if hours > 12:
    hours -= 12
  elif hours == 0:
    hours = 12
  minutes = time % 100
  return str(hours) + ':' + ("0" if minutes < 10 else "") + str(minutes) + ampm