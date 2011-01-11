#!/usr/bin/env python
import sys
import helper_utils
from getopt import getopt, GetoptError
from os import environ


def test_openoffice(hostname, port):
  try:
    helper_utils.getServiceManager(hostname, port)
    return True
  except Exception, err:
    print err
    return False


def main():
  try:
    opt_list, arg_list = getopt(sys.argv[1:], "",
                                ["port=","hostname=","uno_path="])
  except GetoptError, e:
    print >> sys.stderr, "%s \nUse --port and --hostname" % e
    sys.exit(2)

  for opt, arg in opt_list:
    if opt == "--port":
      port = arg
    elif opt == "--hostname":
      hostname = arg
    elif opt == "--uno_path":
      environ["uno_path"] = arg

  print test_openoffice(hostname, port)


if __name__ == "__main__":
  main()
