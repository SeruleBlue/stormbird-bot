from random import random
import logging
import re

logging.basicConfig(level=logging.INFO)

isInit = False
SU_FILE_NAME = 'data/superusers.txt'
superUserList = []

def isSuperUser(author):
  """ Returns if the given author is listed in the superusers list. """
  global isInit
  if not isInit:
    try:
      global superUserList
      file = open(SU_FILE_NAME, 'r')
      superUserList = [x.strip('\n') for x in file.readlines()]
      isInit = True
    except Exception as e:
      log('Util', 'Error when loading superusers: ' + e)
      return
  return str(author) in superUserList

def isValidUniqueUser(user):
  if user is None:
    return False
  return re.match('.*#[0-9]{4}', user) is not None

def sw(message, value):
  """ Short version of startswith to check for !commands """
  return message.content.startswith(value)

def getArg(argsString, index):
  argsList = argsString.split()
  return None if len(argsList) <= index else argsList[index]

def roll(chance):
  return random() < chance

def log(label, message):
  print('[' + label + '] ' + message)