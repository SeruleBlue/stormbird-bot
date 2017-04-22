import logging

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

def getArg(args, index):
  args = args.split()
  return None if len(args) <= index else args[index]

def log(label, message):
  print('[' + label + '] ' + message)