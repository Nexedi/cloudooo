#!/usr/bin/env python

import sys
import unittest
from argparse import ArgumentParser
from time import sleep
from subprocess import Popen
from ConfigParser import ConfigParser
from os import chdir, path, environ, curdir, remove
from psutil import Process
from signal import SIGQUIT

ENVIRONMENT_PATH = path.abspath(path.dirname(__file__))


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


def run():
  parser = ArgumentParser(description="Unit Test Runner for Cloudooo")
  parser.add_argument('server_cloudooo_conf')
  parser.add_argument('test_name')
  parser.add_argument('--timeout_limit', dest='timeout_limit',
                      type=long, default=30,
                      help="Timeout to waiting for the cloudooo stop")
  parser.add_argument('--paster_path', dest='paster_path',
                      default='paster',
                      help="Path to Paster script")
  namespace = parser.parse_args()

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
  if not path.exists(path.join(ENVIRONMENT_PATH,
                               '%s%s' % (test_name, python_extension))):
    exit("%s not exists\n" % test_name)

  from cloudoooTestCase import startFakeEnvironment, stopFakeEnvironment

  sys.path.append(ENVIRONMENT_PATH)

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
    chdir(ENVIRONMENT_PATH)
    try:
      TestRunner(verbosity=2).run(suite)
    finally:
      process.send_signal(SIGQUIT)
      process.wait()
  elif OPENOFFICE:
    chdir(ENVIRONMENT_PATH)
    openoffice = startFakeEnvironment(conf_path=server_cloudooo_conf)
    try:
      TestRunner(verbosity=2).run(suite)
    finally:
      stopFakeEnvironment()
  else:
    chdir(ENVIRONMENT_PATH)
    TestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
  run()
