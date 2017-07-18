from discord import Game
from discord.ext.commands import Bot
from modules import event
from modules import reaction
from modules import util
from modules import wildmagic
from modules import deckofmanythings
from modules import raid
from modules import markov
from random import randint
from random import choice
import asyncio
import datetime
import logging
import re

logging.basicConfig(level=logging.INFO)
stormbird = Bot(command_prefix="!", description="!help for commands")

FILE_NAME_KEY = 'data/key.txt'
startTime = None

playing = ["Factorio", "Ace Combat 04", "Ace Combat 5", "Ace Combat Zero",
           "Avian Attorney", "Danganronpa", "Cyberslide", "A Stroll Through Slipspace",
           "Terraria", "Stardew Valley", "PyCharm", "Flash CS6", "FlashDevelop",
           "ArtStudio", "WildStar", "Shenzhen I/O", "GIMP", "IntelliJ"]

@stormbird.event
@asyncio.coroutine
def on_ready():
  ### Set up modules
  yield from wildmagic.loadEffects()
  yield from deckofmanythings.loadEffects()
  yield from raid.loadEffects()
  global startTime
  startTime = datetime.datetime.now()
  util.log('Stormbird', 'Client ready.')
  yield from change_playing()

@asyncio.coroutine
def change_playing():
  global playing
  yield from stormbird.change_presence(game=Game(name=choice(playing)))
  yield from asyncio.sleep(randint(3600, 28800))  # 1-8 hrs
  yield from change_playing()

@stormbird.event
@asyncio.coroutine
def on_message(message):
  nameUnique = str(message.author)
  if nameUnique == 'stormbird#3705' or nameUnique == 'stormbird-dev#0449':
    return

  if not (yield from wildmagic.checkOngoingEffect(stormbird, message)):
    return

  yield from reaction.on_message(stormbird, message)
  #yield from timezone.convertTimezone(stormbird, message)
  yield from event.on_message(stormbird, message)

  if message.content.startswith('!help'):
    yield from help(message)
  elif message.content.startswith('!roll'):
    yield from roll(message)
  elif message.content.startswith('!wild'):
    yield from wildmagic.getAndApplyEffect(stormbird, message)
  elif message.content.startswith('!deck'):
    yield from deckofmanythings.startDraw(stormbird, message)
  elif message.content.startswith('!dungeon'):
    yield from raid.getStory(stormbird, message)
  elif message.content.startswith('!corpus'):
    yield from markov.loadCorpus(stormbird, message)
  elif message.content.startswith('!status'):
    yield from stormbird.send_message(message.channel, 'Stormbird is up since ' + str(startTime) + '.')
    return
  elif message.content.startswith('!uptime'):
    diffTime = datetime.datetime.now() - startTime
    yield from stormbird.send_message(message.channel, 'Stormbird is up for ' + str(diffTime) + '.')
    return

@asyncio.coroutine
def help(message):
  reply = ("Hello, " + message.author.display_name + "! I'm Serule's minion. Try these:\n"
           "`!deck 1`"
           "`!dungeon`"
           "`!event`\n"
           "`!reaction`"
           "`!roll`\n"
           "`!roll 2d8`\n"
           "`!roll 20`\n"
           "`!status`"
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