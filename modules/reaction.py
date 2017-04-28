from discord.ext.commands import Bot
from modules import util
from tinydb import TinyDB, where
import asyncio

"""
DATABASE db-reaction
username    | emoji | chance
Serule#9451 | 🐦    | 25
"""
DB_NAME = "data/db-reaction.json"
db = None

@asyncio.coroutine
def on_message(bot: Bot, message):
  # Ensure db is setup
  global db
  if db is None:
    db = TinyDB(DB_NAME)

  # Apply reactions if applicable
  yield from applyReaction(bot, message)

  # Quit if not superuser, then do special commands
  if not util.isSuperUser(message.author):
    return
  if util.sw(message, '!reaction add') or util.sw(message, '!reaction remove'):
    yield from updateReaction(bot, message)
  elif util.sw(message, '!reaction list'):
    yield from listReactions(bot, message)
  elif util.sw(message, '!reaction purge'):
    yield from purge(bot, message)
  elif util.sw(message, '!reaction'):
    yield from help(bot, message)

"""
Updates a reaction.
!reaction add user#1234 emoji chance
!reaction remove user#1234 emoji
"""
@asyncio.coroutine
def updateReaction(bot: Bot, message):
  try:
    isRemove = util.getArg(message.content, 1).lower() == 'remove'
  except Exception:
    yield from bot.send_message(message.channel, "❌ Check your arguments.")
    return
  # Grab and validate username
  username = ''
  try:
    username = util.getArg(message.content, 2)
    if username is None:
      yield from bot.send_message(message.channel, "❌ Send me a name, please.")
      return
    if not util.isValidUniqueUser(username):
      yield from bot.send_message(message.channel, "❌ Send me the full name (" +
                                  username + "#XXXX), please.")
      return
  except ValueError:
    yield from bot.send_message(message.channel, "❌ The name (" +
                                username + ") is invalid.")
  username = username.lower()
  # Grab and validate emoji
  emoji = util.getArg(message.content, 3)
  if emoji is None:
    yield from bot.send_message(message.channel, "❌ Send me an emoji, please.")
    return
  # Grab and validate chance
  chance = 0
  if not isRemove:
    try:
      chance = int(util.getArg(message.content, 4))
      if chance is None:
        yield from bot.send_message(message.channel, "❌ Send me a chance, please.")
        return
    except Exception:
      yield from bot.send_message(message.channel, "❌ The chance is invalid.")
      return
    if chance < 0 or chance > 100:
      yield from bot.send_message(message.channel, "❌ The chance (" +
                                  str(chance) + ") needs to be within 0 and 100.")
      return

  if username is None or emoji is None or (chance is None and not isRemove):
    yield from bot.send_message(message.channel, "❌ One of the args is None!")
    return

  if isRemove:
    db.remove((where('username') == username) & (where('emoji') == emoji))
    yield from bot.send_message(message.channel, "✅ Removed the " + emoji +
                                " proc from " + util.getArg(message.content, 2) + ".")
  else:
    if not db.search(
      (where('username') == username) & (where('emoji') == emoji)):
      db.insert({
        'username': username,
        'emoji': emoji,
        'chance': chance
      })
      yield from bot.send_message(message.channel, "✅ Gave " +
                                  util.getArg(message.content, 2) + " a " +
                                  str(chance) + "% chance to proc " + emoji + ".")
    else:
      db.update(
        {'chance': chance},
        (where('username') == username) & (where('emoji') == emoji)
      )
      yield from bot.send_message(message.channel, "✅ Updated " +
                                  util.getArg(message.content, 2) + " with a " +
                                  str(chance) + "% chance to proc " + emoji + ".")
  return

"""
Have the bot apply a reaction based on the contents of the table.
<no command>
"""
@asyncio.coroutine
def applyReaction(bot: Bot, message):
  global db
  rows = db.search(where('username') == str(message.author).lower())
  if rows:
    for row in rows:
      if util.roll(row['chance'] / 100):
        try:
          yield from bot.add_reaction(message, row['emoji'])
        except Exception:
          None

"""
Spits out a list of all known reactions.
!reaction list
"""
@asyncio.coroutine
def listReactions(bot: Bot, message):
  rows = db.all()
  if not rows:
    response = 'No reactions saved yet.'
  else:
    response = 'Stored reactions:'
    for row in rows:
      response += '\n' + row['username'] + '\t' + row['emoji'] + '\t' + str(row['chance']) + '%'
  yield from bot.send_message(message.channel, response)

"""
Purges all reactions.
!reaction purge
"""
@asyncio.coroutine
def purge(bot, message):
  db.purge()
  yield from bot.send_message(message.channel, "✅ Reactions cleared.")

"""
Displays help.
!reaction
"""
@asyncio.coroutine
def help(bot, message):
  yield from bot.send_message(message.channel,
                              ("This handles automatic reactions!\n"
                               "`!reaction add Name#1234 🐦 50`\n"
                               "`!reaction remove Name#1234 🐦`\n"
                               "`!reaction list`\n"
                               "`!reaction purge`"))