import asyncio
import logging
import markovify
from modules import util

logging.basicConfig(level=logging.INFO)

DEBUG = 'Markov'
FILE_NAME_CORPUS = 'data/corpus.txt'

text_model = None

@asyncio.coroutine
def loadEffects():
  try:
    # Get raw text as string.
    with open(FILE_NAME_CORPUS) as file:
      text = file.read()
    # Build the model.
    global text_model
    text_model = markovify.Text(text)
    file.close()
  except Exception as e:
    util.log(DEBUG, "Error when loading lines: " + e)
    return

@asyncio.coroutine
# !say 2
def makeSentence(bot, message):
  try:
    num = int(util.getArg(message.content, 1))
    if num > 10:
      num = 10
    if num < 1:
      num = 1
  except:
    num = 1

  reply = ''
  for i in range(num):
    reply += text_model.make_sentence() + ' '
  yield from bot.send_message(message.channel, reply)