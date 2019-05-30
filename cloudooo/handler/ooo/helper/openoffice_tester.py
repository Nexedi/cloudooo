#!/usr/bin/env python
import sys
import helper_util
from getopt import getopt, GetoptError

try:
  import json
except ImportError:
  import simplejson as json


def test_openoffice(connection, uno_path, office_binary_path, terminate=False):
  import pyuno
  try:
    sm = helper_util.getServiceManager(connection, uno_path, office_binary_path)
    if terminate:
      try:
        sm.createInstance("com.sun.star.frame.Desktop").terminate()
      except pyuno.getClass("com.sun.star.beans.UnknownPropertyException"):
        pass
      except pyuno.getClass("com.sun.star.lang.DisposedException"):
        pass
    return True
  except pyuno.getClass("com.sun.star.connection.NoConnectException"):
    return False


def main():
  try:
    opt_list, arg_list = getopt(sys.argv[1:], "",
                                ["connection=", "uno_path=",
                                 "office_binary_path=",
                                 "terminate"])
  except GetoptError as e:
    sys.stderr.write("%s \nUse --connection" % e)
    sys.exit(2)

  connection = uno_path = office_binary_path = None
  terminate = False
  for opt, arg in opt_list:
    if opt == "--connection":
      connection = arg
    elif opt == "--uno_path":
      uno_path = arg
      if uno_path not in sys.path:
        sys.path.append(uno_path)
    elif opt == "--office_binary_path":
      office_binary_path = arg
    elif opt == "--terminate":
      terminate = True

  output = json.dumps(test_openoffice(connection,
                               uno_path, office_binary_path,
                                      terminate=terminate))
  sys.stdout.write(output)

if __name__ == "__main__":
  helper_util.exitOverAbort(main)