#!/usr/bin/env python
import sys
import helper_util
from getopt import getopt, GetoptError
import time
import uno
NoConnectException = uno.getClass("com.sun.star.connection.NoConnectException")

def test_openoffice(hostname, port):
  # increase count if NoConnectException raised
  count = 10
  try:
    for i in range(count - 1):
      try:
        helper_util.getServiceManager(hostname, port)
        break
      except NoConnectException:
        if i == count - 2:
          helper_util.getServiceManager(hostname, port)
      time.sleep(1)
    return True
  except:
    import traceback
    sys.stderr.write(traceback.format_exc())
    return False


def main():
  try:
    opt_list, arg_list = getopt(sys.argv[1:], "",
                                ["port=", "hostname=", "uno_path=",
                                 "office_binary_path="])
  except GetoptError, e:
    print >> sys.stderr, "%s \nUse --port and --hostname" % e
    sys.exit(2)

  port = hostname = uno_path = office_binary_path = None
  for opt, arg in opt_list:
    if opt == "--port":
      port = arg
    elif opt == "--hostname":
      hostname = arg
    elif opt == "--uno_path":
      uno_path = arg
    elif opt == "--office_binary_path":
      office_binary_path = arg

  print test_openoffice(hostname, port, uno_path, office_binary_path)


if __name__ == "__main__":
  main()
