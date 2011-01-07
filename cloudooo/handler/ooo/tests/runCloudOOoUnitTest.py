#!/usr/bin/env python

import sys
import unittest
from argparse import ArgumentParser
from time import sleep
from cloudooo.handler.ooo.utils.utils import socketStatus
from ConfigParser import ConfigParser
from os import chdir, path, environ, curdir
from subprocess import Popen, PIPE
import tempfile
import os

ENVIRONMENT_PATH = path.abspath(path.dirname(__file__))


def wait_liberate_port(hostname, port, timeout_limit=30):
  for n in range(timeout_limit):
    if not socketStatus(hostname, port):
      break
    sleep(1)


def wait_use_port(hostname, port, timeout_limit=30):
  for n in range(timeout_limit):
    if socketStatus(hostname, port):
      break
    sleep(1)


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
  openoffice_port = int(config.get("app:main", "openoffice_port"))
  xvfb_port = int(config.get("app:main", "virtual_display_port"))
  xvfb_display_id = int(config.get("app:main", "virtual_display_id"))
  hostname = config.get("app:main", "application_hostname")
  server_port = int(config.get("server:main", "port"))
  run_dir = config.get('app:main', 'working_path')
  module = __import__(test_name)
  if not hasattr(module, "test_suite"):
    exit("No test suite to run, exiting immediately")


  DAEMON = getattr(module, 'DAEMON', False)
  OPENOFFICE = getattr(module, 'OPENOFFICE', False)
  XVFB = getattr(module, 'XVFB', False)

  TestRunner = unittest.TextTestRunner
  suite = unittest.TestSuite()
  suite.addTest(module.test_suite())

  if DAEMON:
    fd, pid_filename = tempfile.mkstemp()
    command = [paster_path, "serve", '--daemon', '--pid-file', pid_filename,
               server_cloudooo_conf]
    process = Popen(command)
    wait_use_port(hostname, openoffice_port)
    wait_use_port(hostname, server_port)
    chdir(ENVIRONMENT_PATH)
    try:
      TestRunner(verbosity=2).run(suite)
    finally:
      command = [paster_path, 'serve', '--stop-daemon', '--pid-file',
                 pid_filename]
      stop_process = Popen(command)
      stop_process.communicate()
      # pid file is destroyed by paster
  elif OPENOFFICE:
    chdir(ENVIRONMENT_PATH)
    openoffice, xvfb = startFakeEnvironment(conf_path=server_cloudooo_conf)
    try:
      TestRunner(verbosity=2).run(suite)
    finally:
      stopFakeEnvironment()
  elif XVFB:
    chdir(ENVIRONMENT_PATH)
    xvfb = startFakeEnvironment(start_openoffice=False,
                                conf_path=server_cloudooo_conf)
    try:
      TestRunner(verbosity=2).run(suite)
    finally:
      stopFakeEnvironment(stop_openoffice=False)
  else:
    chdir(ENVIRONMENT_PATH)
    TestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
  run()
