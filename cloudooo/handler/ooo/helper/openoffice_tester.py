#!/usr/bin/env python
import sys
import helper_util
from getopt import getopt, GetoptError


def test_openoffice(hostname, port):
  try:
    helper_util.getServiceManager(hostname, port)
    return True
  except Exception, err:
    print err
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
