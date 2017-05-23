from discord.ext.commands import Bot
from modules import util
import random
import asyncio
import logging
import time

logging.basicConfig(level=logging.INFO)

DEBUG = 'DoMT'
DIRECTORY = 'data/deckofmanythings'
FILE_NAME_EFFECTS = DIRECTORY + '/dnd_domtEffects.txt'
FILE_NAME_FLAVOR = DIRECTORY + '/dnd_domtFlavor.txt'
COOLDOWN_S = 7200

effectsTable = {}     # dictionary of card name to effect
flavorList = []
userStatus = {}       # dictionary of username to [timeOfLastRequest, effectName=]

currentDraws = 0
currentName = None

@asyncio.coroutine
def loadEffects():
  try:
    global flavorList
    file = open(FILE_NAME_EFFECTS, 'r')
    effects = [x.strip('\n') for x in file.readlines()]
    for effectPair in effects:
      name, effect = effectPair.split(':')
      effectsTable[name] = effect[1:]
    file.close()
    file = open(FILE_NAME_FLAVOR, 'r')
    flavorList = [x.strip('\n') for x in file.readlines()]
    file.close()
  except Exception as e:
    util.log(DEBUG, "Error when loading effects: " + e)
    return

@asyncio.coroutine
def startDraw(bot: Bot, message):
  global currentDraws, currentName
  if currentDraws > 0:
    yield from bot.send_message(message.channel, "Wait a moment. " + currentName + " is drawing...")
    return

  name = message.author.display_name
  superUser = util.isSuperUser(message.author)
  if superUser and util.getArg(message.content, 1) == "reset":
    yield from bot.send_message(message.channel, "✅ The Deck of Many Things has been reset.")
    loadEffects()
    return

  # check cooldown
  if name not in userStatus:
    userStatus[name] = [0, None]
  elif not superUser:
    cd = getCd(name)
    if cd > 0:
      unit = 'second'
      if cd > 60:
        unit = 'minute'
        cd = int(cd / 60)
      elif cd > 3600:
        unit = 'hour'
        cd = int(cd / 3600)

      return (yield from bot.send_message(message.channel, name + "'s Deck of Many Things is on cooldown. Wait " + str(cd) +
                                    " more " + pl(cd, unit) + "."))

  draws = util.getArg(message.content, 1)
  if not draws:
    return (yield from bot.send_message(message.channel, "❌ You must state a number of cards to draw. (1-5)"))
  try:
    draws = int(draws)
  except:
    return (yield from bot.send_message(message.channel, "❌ You must state a number of cards to draw. (1-5)"))
  if draws < 1 or draws > 5:
    return (yield from bot.send_message(message.channel, "❌ You must draw between 1 and 5 cards."))

  userStatus[name][0] = int(time.time())
  currentName = name
  currentDraws = draws
  yield from getAndApplyEffect(bot, message)

# As superuser, do
#   !deck <effectname>
@asyncio.coroutine
def getAndApplyEffect(bot: Bot, message):
  name = message.author.display_name

  global currentDraws, currentName
  effectName, effectDesc = random.choice(list(effectsTable.items()))


  yield from bot.send_message(message.channel, (random.choice(flavorList).replace('{name}', name) + ' (*' +
                              str(currentDraws) + ' left*)'))
  yield from bot.send_typing(message.channel)
  yield from asyncio.sleep(5)

  response = '(**' + effectName + '**) ' + effectDesc.replace('{name}', name)
  yield from bot.send_message(message.channel, response)
  try:
    yield from bot.send_file(message.channel, DIRECTORY + '/' + effectName.lower() + '.png')
  except:
    return

  if effectName == "Fool" or effectName == "Jester":
    del effectsTable[effectName]
    currentDraws += (1 if effectName == "Fool" else 2)
  elif effectName == "Void" or effectName == "Donjon":
    currentDraws = 1

  if currentDraws > 0:
    currentDraws -= 1
    if currentDraws > 0:
      yield from asyncio.sleep(2)
      yield from getAndApplyEffect(bot, message)
    else:
      currentName = None
  return

def getCd(name):
  if name not in userStatus:
    return 0
  return (userStatus[name][0] + COOLDOWN_S) - int(time.time())

def pl(num, word):
  return word if num == 1 else word + 's'