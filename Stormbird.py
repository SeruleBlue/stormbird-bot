from discord.ext.commands import Bot
from discord import emoji
from random import randint
import logging

logging.basicConfig(level=logging.INFO)
stormbird = Bot(command_prefix="!", description="Type !help for commands")

@stormbird.event
async def on_ready():
  print("Client logged in")


@stormbird.event
async def on_message(message):

  if message.content.startswith('!help'):
    await help(message)
    return
  if message.content.startswith('!roll'):
    await roll(message)
    return

  name = str.lower(message.author.display_name)
  nameUnique = str(message.author)
  if name == 'stormbird':
    return
  if name == 'ayd' or nameUnique == 'AYD#5916':
    if randint(0, 4) == 0:
      await stormbird.add_reaction(message, '🐰')
    return
  if name == 'vulpes':
    return await stormbird.add_reaction(message, '👻')

async def help(message):
  reply = ("Hello, " + message.author.display_name + "! I'm Serule's minion. Try these:\n"
           "`!roll`\n"
           "`!roll 2d8`")
  await stormbird.send_message(message.channel, reply)

async def roll(message):
  """Rolls a dice in NdN format."""

  args = str.split(message.content)
  if len(args) > 1 and args[1] is not None:
    dice = args[1]
  else:
    dice = '1d20'

  try:
    rolls, limit = map(int, dice.split('d'))
  except Exception:
    await stormbird.send_message(message.channel, 'Try writing it in this format: NdN')
    return

  if rolls < 1 or limit < 1:
    return
  if rolls > 1000 or limit > 999999999:
    await stormbird.send_message(message.channel, "I'm not doing that much.")
    return

  result = ', '.join(str(randint(1, limit)) for r in range(rolls))
  await stormbird.send_message(message.channel, result)


stormbird.run("MzA0MTExMzQ0NDUyMzcwNDM0.C9h5Sw.g4alaSXIYtTpTnqJDyoXrggGWJc")
