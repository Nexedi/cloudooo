#!/usr/bin/env python
import sys
import helper_util
from getopt import getopt, GetoptError

try:
  import json
except ImportError:
  import simplejson as json


def test_openoffice(hostname, port, uno_path, office_binary_path):
  import pyuno
  try:
    helper_util.getServiceManager(hostname, port, uno_path, office_binary_path)
    return True
  except pyuno.getClass("com.sun.star.connection.NoConnectException"):
    return False


def main():
  try:
    opt_list, arg_list = getopt(sys.argv[1:], "",
                                ["port=", "hostname=", "uno_path=",
                                 "office_binary_path="])
  except GetoptError as e:
    sys.stderr.write("%s \nUse --port and --hostname" % e)
    sys.exit(2)

  port = hostname = uno_path = office_binary_path = None
  for opt, arg in opt_list:
    if opt == "--port":
      port = arg
    elif opt == "--hostname":
      hostname = arg
    elif opt == "--uno_path":
      uno_path = arg
      if uno_path not in sys.path:
        sys.path.append(uno_path)
    elif opt == "--office_binary_path":
      office_binary_path = arg

  output = json.dumps(test_openoffice(hostname, port,
                               uno_path, office_binary_path))
  sys.stdout.write(output)

if __name__ == "__main__":
  helper_util.exitOverAbort(main)