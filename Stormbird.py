from discord.ext.commands import Bot
from discord import emoji
from random import randint
import logging
from modules import wildmagic
import asyncio

logging.basicConfig(level=logging.INFO)
stormbird = Bot(command_prefix="!", description="Type !help for commands")


@stormbird.event
@asyncio.coroutine
def on_ready():
  print("Client logged in")

  ### Set up modules
  yield from wildmagic.loadEffects()

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
           "`!roll 2d8`")
  yield from stormbird.send_message(message.channel, reply)

@asyncio.coroutine
def roll(message):
  """Rolls a dice in NdN format."""

  args = str.split(message.content)
  if len(args) > 1 and args[1] is not None:
    dice = args[1]
  else:
    dice = '1d20'

  try:
    rolls, limit = map(int, dice.split('d'))
  except Exception:
    yield from stormbird.send_message(message.channel, 'Try writing it in this format: NdN')
    return

  if rolls < 1 or limit < 1:
    return
  if rolls > 1000 or limit > 999999999:
    yield from stormbird.send_message(message.channel, "I'm not doing that much.")
    return

  result = ', '.join(str(randint(1, limit)) for r in range(rolls))
  yield from stormbird.send_message(message.channel, result)


stormbird.run("MzA0MTExMzQ0NDUyMzcwNDM0.C9h5Sw.g4alaSXIYtTpTnqJDyoXrggGWJc")
