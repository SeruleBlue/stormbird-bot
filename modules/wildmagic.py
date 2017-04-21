from discord.ext.commands import Bot
from random import randint
import logging
import time
import asyncio

logging.basicConfig(level=logging.INFO)

FILE_NAME = 'data/dnd_wildMagic.txt'
COOLDOWN_S = 60

effectsTable = {}     # dictionary of number to effect
userStatus = {}       # dictionary of username to [timeOfLastRequest, effectName=]

@asyncio.coroutine
def loadEffects():
  try:
    file = open(FILE_NAME, 'r')
    effects = [x.strip('\n') for x in file.readlines()]
    for effect in effects:
      die0 = effect[0:2]
      die1 = effect[3:5]
      die0 = die0.lstrip('0') if die0 != "00" else 0
      die1 = die1.lstrip('0') if die1 != "00" else 0
      effectsTable[int(die0)] = effect[6:]
      effectsTable[int(die1)] = effect[6:]
  except Exception as e:
    print('[Wild Magic] Error when loading effects:', e)
    return
  print('[Wild Magic] Module ready!')


# As superuser, do
#   !wild <roll#>
@asyncio.coroutine
def getAndApplyEffect(bot: Bot, message):
  name = message.author.display_name
  superUser = str(message.author) == "Serule#9451"

  # check cooldown
  if name not in userStatus:
    userStatus[name] = [0, None]
  elif not superUser:
    cd = getCd(name)
    if cd > 0:
      return (yield from bot.send_message(message.channel, name + "'s Wild Magic is on cooldown. Wait " + str(cd) +
                                    " more " + pl(cd, 'second') + "."))
  userStatus[name][0] = int(time.time())

  roll = randint(0, 100)

  if superUser:
    args = str.split(message.content)
    if len(args) > 1:
      roll = int(args[1])

  # special cases
  if roll == 49 or roll == 50:
    userStatus[name][1] = 'mute'
  elif roll == 51 or roll == 52:
    userStatus[name][1] = 'shield'
  elif roll == 57 or roll == 58:
    userStatus[name][1] = 'flameBurst'
  elif roll == 61 or roll == 62:
    userStatus[name][1] = 'allCaps'
  elif roll == 71 or roll == 72:
    userStatus[name][1] = 'resistance'
  elif roll == 25 or roll == 26:
    userStatus[name][1] = 'eye'
  elif roll == 75 or roll == 76:
    userStatus[name][1] = 'light'
  elif roll == 79 or roll == 80:
    userStatus[name][1] = 'butterfly'
  elif roll == 33 or roll == 34:
    userStatus[name][1] = 'maxDamageSpell'
  elif roll == 89 or roll == 90:
    userStatus[name][1] = 'invisible'
  elif roll == 91 or roll == 92:
    userStatus[name][1] = 'revive'
  elif roll == 93 or roll == 94:
    userStatus[name][1] = 'big'
  elif roll == 95 or roll == 96:
    userStatus[name][1] = 'vulnerable'
  elif roll == 97 or roll == 98:
    userStatus[name][1] = 'music'
  elif roll == 43 or roll == 44:
    userStatus[name][1] = 'teleport'
  elif roll == 47 or roll == 48:
    userStatus[name][1] = 'unicorn'

  response = '(' + str(roll) + ') ' + effectsTable[roll].replace('{name}', name)
  return (yield from bot.send_message(message.channel, response))


# As superuser, do
#   !wild clear
# returns False if an effect will cause the message to be interrupted
@asyncio.coroutine
def checkOngoingEffect(bot: Bot, message):
  name = message.author.display_name

  superUser = str(message.author) == "Serule#9451"
  if superUser:
    args = str.split(message.content)
    if len(args) > 1:
      if args[1] == 'clear':    # remove all statuses and cooldowns
        userStatus.clear()
        return

  if name not in userStatus or userStatus[name][1] is None:
    return True

  cd = getCd(name)

  if cd <= 0:
    userStatus[name][1] = None
    return True


  effectName = userStatus[name][1]
  if effectName == 'mute':
    yield from bot.send_message(message.channel, "💕 Pink bubbles float out of " + name + "'s mouth! 💕 " +
                           "(" + str(cd) + "s)")
    try:
      yield from bot.delete_message(message)
    except Exception as e:
      print("[Wild Magic] Couldn't delete a message.")
    return False
  elif effectName == 'shield':
    yield from bot.add_reaction(message, '🛡')
  elif effectName == 'flameBurst':
    yield from bot.add_reaction(message, '🔥')
  elif effectName == 'resistance':
    yield from bot.add_reaction(message, '💊')
  elif effectName == 'eye':
    yield from bot.add_reaction(message, '👁')
  elif effectName == 'light':
    yield from bot.add_reaction(message, '💡')
  elif effectName == 'butterfly':
    yield from bot.add_reaction(message, '🦋')
  elif effectName == 'maxDamageSpell':
    yield from bot.add_reaction(message, '⚔')
    userStatus[name][1] = None
  elif effectName == 'invisible':
    yield from bot.add_reaction(message, '👻')
  elif effectName == 'revive':
    yield from bot.add_reaction(message, '✝')
  elif effectName == 'big':
    yield from bot.add_reaction(message, '⬆')
  elif effectName == 'vulnerable':
    yield from bot.add_reaction(message, '💔')
  elif effectName == 'music':
    yield from bot.add_reaction(message, '🎶')
  elif effectName == 'teleport':
    yield from bot.add_reaction(message, '🏃')
  elif effectName == 'unicorn':
    yield from bot.add_reaction(message, '🦄')
  elif effectName == 'allCaps':
    if not message.content.isupper():
      yield from bot.send_message(message.channel, name + " must shout when they speak! " +
                             "(" + str(cd) + "s)")
      try:
        yield from bot.delete_message(message)
      except Exception as e:
        print("[Wild Magic] Couldn't delete a message.")
      return False
  return True

def getCd(name):
  if not name in userStatus:
    return 0
  return (userStatus[name][0] + COOLDOWN_S) - int(time.time())

def pl(num, word):
  return word if num == 1 else word + 's'