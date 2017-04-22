from discord.ext.commands import Bot
from modules import util
from modules import wildmagic
from random import randint
import asyncio
import logging
import re

logging.basicConfig(level=logging.INFO)
stormbird = Bot(command_prefix="!", description="Type !help for commands")

FILE_NAME_KEY = 'data/key.txt'

@stormbird.event
@asyncio.coroutine
def on_ready():
  ### Set up modules
  yield from wildmagic.loadEffects()
  util.print('Stormbird', 'Client ready.')

@stormbird.event
@asyncio.coroutine
def on_message(message):
  nameUnique = str(message.author)
  if nameUnique == 'stormbird#3705':
    return

  if not (yield from wildmagic.checkOngoingEffect(stormbird, message)):
    return

  if message.content.startswith('!help'):
    yield from help(message)
  elif message.content.startswith('!roll'):
    yield from roll(message)
  elif message.content.startswith('!wild'):
    yield from wildmagic.getAndApplyEffect(stormbird, message)
  elif message.content.startswith('!status'):
    yield from stormbird.send_message(message.channel, 'Stormbird is alive.')
    return

  name = str.lower(message.author.display_name)
  if name == 'ayd' or nameUnique == 'AYD#5916':
    if randint(0, 4) == 0:
      yield from stormbird.add_reaction(message, '🐰')
  elif name == 'vulpes':
    yield from stormbird.add_reaction(message, '👻')

@asyncio.coroutine
def help(message):
  reply = ("Hello, " + message.author.display_name + "! I'm Serule's minion. Try these:\n"
           "`!roll`\n"
           "`!roll 2d8`\n"
           "`!roll 20`\n"
           "`!wild`")
  yield from stormbird.send_message(message.channel, reply)

@asyncio.coroutine
def roll(message):
  """Rolls a dice in NdN or N format."""
  rolls = 1   # default times to roll
  limit = 100 # default die faces

  args = str.split(message.content)
  diceArg = util.getArg(message.content, 1)
  if diceArg is not None:
    if re.search('^[0-9]+d[0-9]+$', diceArg) is not None:
      rolls, limit = map(int, diceArg.split('d'))
    elif re.search('^[0-9]+$', diceArg):
      limit = int(diceArg)
    else:
      return

  if rolls < 1 or limit < 1:
    return
  if rolls > 1000 or limit > 999999999:
    yield from stormbird.send_message(message.channel, "I'm not doing that much.")
    return

  result = ', '.join(str(randint(1, limit)) for r in range(rolls))
  yield from stormbird.send_message(message.channel, result)

""" Read the key and run the bot. """
try:
  f = open(FILE_NAME_KEY, 'r')
  key = f.readline().strip('\n')
  f.close()
  stormbird.run(key)
except Exception as e:
  util.log("Main", "Key read error: " + e)