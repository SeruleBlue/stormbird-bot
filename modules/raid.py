from discord.ext.commands import Bot
from modules import util
import random
import asyncio
import logging
import time
import re

logging.basicConfig(level=logging.INFO)

DEBUG = 'Raid'
FILE_NAME_LINES = 'data/raid.txt'
COOLDOWN_S = 60

storyLines = []       # chronological list of lists of potential lines
userStatus = {}       # dictionary of username to [timeOfLastRequest, effectName=]

tellingStory = False

@asyncio.coroutine
def loadEffects():
  try:
    file = open(FILE_NAME_LINES, 'r')
    lines = [x.strip('\n') for x in file.readlines()]
    group = []
    for line in lines:
      if line == "":
        storyLines.append(group)
        group = []
      else:
        group.append(line)
    storyLines.append(group)
    file.close()
  except Exception as e:
    util.log(DEBUG, "Error when loading lines: " + e)
    return

@asyncio.coroutine
def getStory(bot: Bot, message):
  name = message.author.display_name
  superUser = util.isSuperUser(message.author)

  global tellingStory
  if tellingStory:
    yield from bot.send_message(message.channel, "*Wait a moment for me to finish this story.*")
    yield from bot.send_typing(message.channel)
    return

  # check cooldown
  if name not in userStatus:
    userStatus[name] = [0, None]
  elif not superUser:
    cd = getCd(name)
    if cd > 0:
      return (yield from bot.send_message(message.channel, name + "'s Wildstar story is on cooldown. Wait " + str(cd) +
                                    " more " + pl(cd, 'second') + "."))
  userStatus[name][0] = int(time.time())

  tellingStory = True

  branch = ''
  stop = False
  for group in storyLines:
    # Check for branch designator
    if re.match("{[A-Z]*}", group[0]):
      if group[0] != branch:
        continue

    line = random.choice(group)
    line = line.replace("{name}", name)
    numbers = re.search("{[0-9]+,[0-9]+}", line)
    if numbers:
      numbers = numbers.group(0)
      numPair = numbers[1:-1].split(",")
      line = line.replace(numbers, str(random.randint(int(numPair[0]), int(numPair[1]))))
    branch = re.search("{[A-Z]*}", line)
    if branch:
      branch = branch.group(0)
      if branch == "{END}":
        stop = True
        line += "\n**The end!**"
      line = line.replace(branch, "")
    else:
      branch = 'NONE'
    yield from bot.send_message(message.channel, line)
    if line != "**The end!**" and not stop:
      yield from bot.send_typing(message.channel)
    yield from asyncio.sleep(random.randint(4, 7))
    if stop:
      break
  tellingStory = False

def getCd(name):
  if name not in userStatus:
    return 0
  return (userStatus[name][0] + COOLDOWN_S) - int(time.time())

def pl(num, word):
  return word if num == 1 else word + 's'