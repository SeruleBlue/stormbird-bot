from discord.ext.commands import Bot
from modules import util
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
LEN_LIMIT = 30
wordDict = []

DIRECTORY = 'data/'
FILE_NAME_DICT = DIRECTORY + '/dictionary.txt'

@asyncio.coroutine
def loadEffects():
  try:
    global wordDict
    wordDict = [[] for i in range(LEN_LIMIT)]
    file = open(FILE_NAME_DICT, 'r')
    words = [x.strip('\n') for x in file.readlines()]
    for word in words:
      if len(word) > LEN_LIMIT:
        continue
      wordDict[len(word)].append(word)
    file.close()
  except Exception as e:
    util.log("Orc", "Error when loading dict: " + e)
    return

# !orc word
@asyncio.coroutine
def getOrcs(bot: Bot, message):
  argsList = message.content.split()
  if len(argsList) == 1:
    return (yield from bot.send_message(message.channel, "❌ You must provide at least one word."))
  yield from bot.send_typing(message.channel)
  output = ""
  for word in argsList[1:]:
    output += (yield from getSingleOrc(word.lower())) + "\n"
  yield from bot.send_message(message.channel, "✨ Showing orcs for: " + " ".join(argsList[1:]) + "\n" + output)

@asyncio.coroutine
def getSingleOrc(word):
  wordList = wordDict[len(word)]
  matches = ""
  for item in wordList:
    if item == word:
      continue
    diffInd = -1
    for i, (a, b) in enumerate(zip(word, item)):
      if a != b:
        # If a difference index was already found, quit
        if diffInd != -1:
          diffInd = -1
          break
        diffInd = i
    if diffInd != -1:
      matches += item[:diffInd] + '**' + item[diffInd] + '**' + item[diffInd + 1:] + ' '

  if matches == "":
    return "\n❌ " + word + "\nNo matches"
  else:
    return "\n✅ " + word + "\n" + matches