#!/usr/bin/env python

import sys
import unittest
from getopt import getopt, GetoptError
from time import sleep
from cloudooo.utils import socketStatus
from ConfigParser import ConfigParser
from os import chdir, path, environ
from subprocess import Popen

ENVIRONMENT_PATH = path.abspath(path.dirname(__file__))

def wait_liberate_port(hostname, port):
  for n in range(timeout_limit):
    if not socketStatus(hostname, port):
      break
    sleep(1)

def wait_use_port(hostname, port):
  for n in range(timeout_limit):
    if socketStatus(hostname, port):
      return
    sleep(1)

def get_partial_log():
  if path.exists(log_path):
    return '\n'.join(open(log_path).read().split('\n')[-30:])
  return ''

def exit(msg):
  sys.stderr.write(msg)
  sys.exit(0) 

def run_test(test_name):
  module = __import__(test_name)
  if not hasattr(module, "test_suite"):
    exit("No test suite to run, exiting immediately")
  TestRunner = unittest.TextTestRunner
  suite = unittest.TestSuite()
  suite.addTest(module.test_suite())
  TestRunner(verbosity=2).run(suite)

def run():
  DAEMON = OPENOFFICE = XVFB = False
  test_name = sys.argv[-1]
  if not path.exists(path.join(ENVIRONMENT_PATH, '%s.py' % test_name)):
    exit("%s not exists\n" % test_name)

  try:
    opt_list, arg_list = getopt(sys.argv[1:-1], "", ["with-daemon",
                                                   "with-openoffice",
                                                   "with-xvfb",
                                                   "log_path=",
                                                   "cloudooo_runner=",
                                                   "server_cloudooo_conf=",
                                                   "timeout_limit="])
  except GetoptError, msg:
    exit(msg.msg)
  
  for opt, arg in opt_list:
    if opt == "--with-daemon":
      DAEMON = True
    elif opt == "--with-openoffice":
      OPENOFFICE = True
    elif opt == "--with-xvfb":
      XVFB = True
    elif opt == "--log_path":
      log_path = arg
    elif opt == "--cloudooo_runner":
      cloudooo_runner = arg
    elif opt == "--server_cloudooo_conf":
      server_cloudooo_conf = arg
      environ["server_cloudooo_conf"] = arg
    elif opt == "--timeout_limit":
      timeout_limit = arg
  
  from cloudoooTestCase import loadConfig, startFakeEnvironment, stopFakeEnvironment
  
  sys.path.append(ENVIRONMENT_PATH)
  chdir(ENVIRONMENT_PATH)
 
  config = ConfigParser()
  config.read(server_cloudooo_conf)
  openoffice_port = int(config.get("app:main", "openoffice_port"))
  xvfb_port = int(config.get("app:main", "virtual_display_port"))
  xvfb_display_id = int(config.get("app:main", "virtual_display_id"))
  hostname = config.get("app:main", "application_hostname")
  server_port = int(config.get("server:main", "port"))
  run_dir = config.get('app:main', 'working_path')

  if DAEMON:
    loadConfig(server_cloudooo_conf)
    Popen([cloudooo_runner, 'start']).communicate()
    wait_use_port(hostname, server_port)
    print get_partial_log()
    try:
      run_test(test_name)
    finally:
      Popen([cloudooo_runner, 'stop']).communicate()
    wait_liberate_port(hostname, server_port)
  elif OPENOFFICE:
    openoffice, xvfb = startFakeEnvironment(conf_path=server_cloudooo_conf)
    run_test(test_name)
    stopFakeEnvironment()
  elif XVFB:
    xvfb = startFakeEnvironment(start_openoffice=False,
                                conf_path=server_cloudooo_conf)
    run_test(test_name)
    stopFakeEnvironment(stop_openoffice=False)
  else:
    loadConfig(server_cloudooo_conf)
    run_test(test_name)

if __name__ == "__main__":
  run()
