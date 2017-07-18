import asyncio
import logging
from modules import util

logging.basicConfig(level=logging.INFO)

DEBUG = 'Markov'
FILE_NAME_CORPUS = 'data/corpus.txt'

@asyncio.coroutine
def loadCorpus(bot, message):
  if not util.isSuperUser(message.author):
    return

  try:
    limit = util.getArg(message.content, 1)
  except:
    return

  util.log(DEBUG, "Calling loadCorpus().")

  yield from bot.send_message(message.channel, "⚠ Collecting corpus with limit: " + limit)
  messages = bot.logs_from(message.channel, limit=int(limit))
  file = open(FILE_NAME_CORPUS, 'wb')
  try:
    msg = yield from messages.iterate()
    while msg:
      wr = msg.content + "\n"
      file.write(wr.encode('utf8'))
      msg = yield from messages.iterate()
  except:
    util.log(DEBUG, "End of log reached.")
  file.close()
  util.log(DEBUG, "Done!")
  yield from bot.send_file(message.author, FILE_NAME_CORPUS)
  yield from bot.send_message(message.channel, "✅ Success, corpus sent!")