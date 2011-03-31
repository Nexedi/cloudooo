#!/usr/bin/env python

import sys
from pkg_resources import resource_filename
import unittest
from time import sleep
from subprocess import Popen
from ConfigParser import ConfigParser
from argparse import ArgumentParser
from os import chdir, path, environ, curdir, remove
from psutil import Process
from signal import SIGQUIT


def wait_use_port(pid, timeout_limit=30):
  process = Process(pid)
  for n in range(timeout_limit):
    if len(process.get_connections()) > 0:
      return True
    sleep(1)
  return False


def exit(msg):
  sys.stderr.write(msg)
  sys.exit(0)


def run(handler_name):
  description = "Unit Test Runner for %s Handler" % handler_name.capitalize()
  parser = ArgumentParser(description=description)
  parser.add_argument('server_cloudooo_conf')
  parser.add_argument('test_name')
  parser.add_argument('--timeout_limit', dest='timeout_limit',
                      type=long, default=30,
                      help="Timeout to waiting for the cloudooo stop")
  parser.add_argument('--paster_path', dest='paster_path',
                      default='paster',
                      help="Path to Paster script")
  namespace = parser.parse_args()
  environment_path = resource_filename("cloudooo.handler.%s" % handler_name,
                                       "/tests")
  server_cloudooo_conf = namespace.server_cloudooo_conf
  test_name = namespace.test_name
  if server_cloudooo_conf.startswith(curdir):
    server_cloudooo_conf = path.join(path.abspath(curdir),
                                     server_cloudooo_conf)
  environ['server_cloudooo_conf'] = server_cloudooo_conf
  paster_path = namespace.paster_path

  python_extension = '.py'
  if test_name[-3:] == python_extension:
    test_name = test_name[:-3]
  full_path = path.join(environment_path, '%s%s' % (test_name,
                                                    python_extension))
  if not path.exists(full_path):
    exit("%s does not exists\n" % full_path)

  from cloudooo.handler.tests.handlerTestCase import startFakeEnvironment
  from cloudooo.handler.tests.handlerTestCase import stopFakeEnvironment

  sys.path.append(environment_path)

  config = ConfigParser()
  config.read(server_cloudooo_conf)
  module = __import__(test_name)
  if not hasattr(module, "test_suite"):
    exit("No test suite to run, exiting immediately")

  DAEMON = getattr(module, 'DAEMON', False)
  OPENOFFICE = getattr(module, 'OPENOFFICE', False)

  TestRunner = unittest.TextTestRunner
  suite = unittest.TestSuite()
  suite.addTest(module.test_suite())

  if DAEMON:
    log_file = '%s/cloudooo_test.log' % config.get('app:main',
                                                   'working_path')
    if path.exists(log_file):
      remove(log_file)
    command = [paster_path, 'serve', '--log-file', log_file,
               server_cloudooo_conf]
    process = Popen(command)
    wait_use_port(process.pid)
    chdir(environment_path)
    try:
      TestRunner(verbosity=2).run(suite)
    finally:
      process.send_signal(SIGQUIT)
      process.wait()
  elif OPENOFFICE:
    chdir(environment_path)
    startFakeEnvironment(conf_path=server_cloudooo_conf)
    try:
      TestRunner(verbosity=2).run(suite)
    finally:
      stopFakeEnvironment()
  else:
    chdir(environment_path)
    TestRunner(verbosity=2).run(suite)
