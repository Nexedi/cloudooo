#!/usr/bin/env python

import sys
import unittest
from getopt import getopt, GetoptError
from time import sleep
from cloudooo.utils import socketStatus
from ConfigParser import ConfigParser
from os import chdir, path, environ, curdir
from subprocess import Popen

ENVIRONMENT_PATH = path.abspath(path.dirname(__file__))

def wait_liberate_port(hostname, port, timeout_limit=10):
  for n in range(timeout_limit):
    if not socketStatus(hostname, port):
      break
    sleep(1)

def wait_use_port(hostname, port, timeout_limit=10):
  for n in range(timeout_limit):
    if socketStatus(hostname, port):
      return
    sleep(1)

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
                                                   "timeout_limit=",
                                                   "paster_path="])
  except GetoptError, msg:
    exit(msg.msg)
  
  paster_path = "paster"

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
      if arg.startswith(curdir):
        arg = path.join(path.abspath(curdir), arg)
      server_cloudooo_conf = arg
      environ["server_cloudooo_conf"] = arg
    elif opt == "--timeout_limit":
      timeout_limit = arg
    elif opt == "--paster_path":
      paster_path = arg
  
  from cloudoooTestCase import loadConfig, startFakeEnvironment, stopFakeEnvironment
  
  sys.path.append(ENVIRONMENT_PATH)
  
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
    command = [paster_path, "serve", server_cloudooo_conf]
    process = Popen(" ".join(command), shell=True)
    wait_use_port(hostname, server_port)
    chdir(ENVIRONMENT_PATH)
    try:
      run_test(test_name)
    finally:
      process.send_signal(1)
      sleep(3)
      process.terminate()
    wait_liberate_port(hostname, server_port)
  elif OPENOFFICE:
    chdir(ENVIRONMENT_PATH)
    openoffice, xvfb = startFakeEnvironment(conf_path=server_cloudooo_conf)
    run_test(test_name)
    stopFakeEnvironment()
  elif XVFB:
    chdir(ENVIRONMENT_PATH)
    xvfb = startFakeEnvironment(start_openoffice=False,
                                conf_path=server_cloudooo_conf)
    run_test(test_name)
    stopFakeEnvironment(stop_openoffice=False)
  else:
    chdir(ENVIRONMENT_PATH)
    loadConfig(server_cloudooo_conf)
    run_test(test_name)

if __name__ == "__main__":
  run()
